"""
Intelligent webhook router for determining message routing.
"""

import re
import httpx
from typing import Dict, Any, Tuple
from datetime import datetime

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class WebhookRouter:
    """
    Intelligent router that analyzes WhatsApp messages and determines
    the appropriate CrewAI workflow for processing.
    Sistema totalmente independente - sem integração N8N.
    """
    
    def __init__(self):
        """Initialize the webhook router."""
        # Agendamento patterns - processados por CrewAI Scheduling Agent
        self.scheduling_patterns = [
            # Scheduling patterns
            r'\b(agendar|consulta|marcar)\b',
            r'\b(horário|horario|disponível|disponivel)\b',
            r'\b(médico|medico|doutor|doutora|dr|dra)\b',
            
            # Confirmation patterns  
            r'\b(confirmar|confirmação|confirmacao)\b',
            r'\b(sim|confirmo|ok|tudo bem)\b',
            
            # Rescheduling patterns
            r'\b(reagendar|remarcar|mudar|trocar)\b',
            r'\b(cancelar|desmarcar)\b',
        ]
        
        # Medical Chat patterns - processados por CrewAI Medical Agent
        self.medical_chat_patterns = [
            # General questions
            r'\b(como|quando|onde|porque|por que|qual)\b',
            r'\b(informação|informacao|dúvida|duvida|ajuda)\b',
            r'\b(oi|olá|ola|bom dia|boa tarde|boa noite)\b',
            
            # General medical info
            r'\b(sintoma|tratamento|medicamento|remédio|remedio)\b',
            r'\b(exame|resultado|procedimento)\b',
            r'\b(orientação|orientacao|cuidados|preparo)\b',
            
            # Medical conditions and symptoms
            r'\b(gripe|resfriado|covid|febre|tosse|dor)\b',
            r'\b(diabetes|pressão|colesterol|coração|cardiaco)\b',
            
            # Clinic information
            r'\b(funcionamento|endereço|endereco|localização|localizacao)\b',
            r'\b(especialidades|convênio|convenio|plano)\b',
        ]
        
        # Emergency patterns that require immediate escalation
        self.emergency_patterns = [
            r'\b(emergência|emergencia|socorro|urgente)\b',
            r'\b(dor no peito|infarto|derrame|avc)\b',
            r'\b(sangramento|hemorragia|desmaio)\b',
            r'\b(falta de ar|respirar|ofegante)\b',
            r'\b(passando mal|muito mal|grave)\b',
            r'\b(dor.*peito|peito.*dor)\b',  # More flexible chest pain pattern
        ]
        
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
    def route_message(self, message_text: str) -> Dict[str, Any]:
        """
        Analyze message and determine routing destination.
        
        Args:
            message_text: Text content of the message
            
        Returns:
            Dict with routing decision and metadata
        """
        if not message_text:
            message_text = ""
            
        # Normalize message text
        normalized_text = self._normalize_message(message_text)
        
        logger.info(
            "Analyzing message for routing",
            message_length=len(message_text),
            message_preview=message_text[:100]
        )
        
        # Check for emergency patterns first
        emergency_score = self._calculate_emergency_score(normalized_text)
        if emergency_score > 0.3:
            return {
                "destination": "crewai",
                "workflow": "emergency_escalation",
                "agent": "emergency_agent",
                "confidence": emergency_score,
                "priority": "high",
                "escalate_immediately": True,
                "reason": f"Emergency keywords detected (score: {emergency_score:.2f})",
                "patterns_matched": self._get_matched_patterns(normalized_text, self.emergency_patterns)
            }
        
        # Calculate scores for Scheduling vs Medical Chat
        scheduling_score = self._calculate_scheduling_score(normalized_text)
        medical_score = self._calculate_medical_score(normalized_text)
        
        # Determine routing based on scores and context
        if scheduling_score > medical_score and scheduling_score > 0.5:
            # Route to CrewAI Scheduling Agent
            workflow = self._determine_scheduling_workflow(normalized_text)
            return {
                "destination": "crewai",
                "workflow": workflow,
                "agent": "scheduling_agent",
                "confidence": scheduling_score,
                "priority": "normal",
                "escalate_immediately": False,
                "reason": f"Scheduling request - {workflow} (score: {scheduling_score:.2f})",
                "patterns_matched": self._get_matched_patterns(normalized_text, self.scheduling_patterns)
            }
        else:
            # Route to CrewAI Medical Agent
            return {
                "destination": "crewai",
                "workflow": "medical_consultation",
                "agent": "medical_agent",
                "confidence": max(medical_score, 0.7),  # Default confidence for medical chat
                "priority": "normal",
                "escalate_immediately": False,
                "reason": f"Medical consultation or general inquiry (medical: {medical_score:.2f}, scheduling: {scheduling_score:.2f})",
                "patterns_matched": self._get_matched_patterns(normalized_text, self.medical_chat_patterns)
            }
    
    def _normalize_message(self, message_text: str) -> str:
        """Normalize message text for better pattern matching."""
        if not message_text:
            return ""
            
        # Convert to lowercase
        text = message_text.lower()
        
        # Remove extra punctuation but keep some for context
        text = re.sub(r'[!]{2,}', '!', text)  # Multiple exclamations to single
        text = re.sub(r'[?]{2,}', '?', text)  # Multiple questions to single
        text = re.sub(r'\.{2,}', '...', text)  # Multiple dots to ellipsis
        
        # Normalize common variations
        text = re.sub(r'\bvc\b', 'você', text)
        text = re.sub(r'\bq\b', 'que', text)
        text = re.sub(r'\btb\b', 'também', text)
        text = re.sub(r'\bpq\b', 'porque', text)
        
        return text.strip()
    
    def _calculate_emergency_score(self, message_text: str) -> float:
        """Calculate emergency score for immediate escalation."""
        matches = 0
        for pattern in self.emergency_patterns:
            if re.search(pattern, message_text, re.IGNORECASE):
                matches += 1
        
        # Emergency patterns are weighted heavily
        base_score = matches / len(self.emergency_patterns)
        
        # Direct critical word matching
        critical_words = ["socorro", "emergência", "emergencia", "infarto", "derrame", "sangramento", "urgente"]
        for word in critical_words:
            if word in message_text:
                base_score += 0.4
        
        # Additional emergency indicators
        if "passando mal" in message_text or "muito mal" in message_text:
            base_score += 0.3
                
        return min(base_score, 1.0)
    
    def _calculate_scheduling_score(self, message_text: str) -> float:
        """Calculate confidence score for Scheduling Agent routing."""
        pattern_matches = 0
        for pattern in self.scheduling_patterns:
            if re.search(pattern, message_text, re.IGNORECASE):
                pattern_matches += 1
        
        # Base score from pattern matches
        base_score = pattern_matches / len(self.scheduling_patterns)
        
        # Boost score for explicit scheduling language
        scheduling_words = ["agendar", "marcar", "consulta", "médico", "horário", "exame"]
        scheduling_score = sum(0.3 for word in scheduling_words if word in message_text)
            
        # Boost score for confirmation language
        confirmation_words = ["confirmar", "sim", "ok", "confirmação"]
        confirmation_score = sum(0.25 for word in confirmation_words if word in message_text)
        
        # Boost for rescheduling/cancellation
        reschedule_words = ["reagendar", "remarcar", "cancelar", "mudar", "trocar"]
        reschedule_score = sum(0.3 for word in reschedule_words if word in message_text)
            
        total_score = base_score + scheduling_score + confirmation_score + reschedule_score
        return min(total_score, 1.0)
    
    def _calculate_medical_score(self, message_text: str) -> float:
        """Calculate confidence score for Medical Agent routing."""
        pattern_matches = 0
        for pattern in self.medical_chat_patterns:
            if re.search(pattern, message_text, re.IGNORECASE):
                pattern_matches += 1
        
        # Base score from pattern matches
        base_score = pattern_matches / len(self.medical_chat_patterns)
        
        # Boost score for question words
        question_words = ["como", "quando", "onde", "porque", "qual", "que", "quem"]
        question_score = sum(0.1 for word in question_words if word in message_text)
            
        # Boost score for greetings
        greeting_words = ["oi", "olá", "bom dia", "boa tarde", "boa noite", "hello"]
        greeting_score = sum(0.08 for word in greeting_words if word in message_text)
        
        # Boost for medical information requests
        medical_words = ["sintoma", "tratamento", "medicamento", "exame", "orientação"]
        medical_score = sum(0.12 for word in medical_words if word in message_text)
        
        # Boost for clinic information requests  
        clinic_words = ["funcionamento", "endereço", "especialidades", "convênio"]
        clinic_score = sum(0.1 for word in clinic_words if word in message_text)
            
        total_score = base_score + question_score + greeting_score + medical_score + clinic_score
        return min(total_score, 1.0)
    
    def _get_matched_patterns(self, message_text: str, patterns: list) -> list:
        """Get list of patterns that matched the message."""
        matched = []
        for pattern in patterns:
            if re.search(pattern, message_text, re.IGNORECASE):
                matched.append(pattern)
        return matched
    
    async def route_webhook_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route webhook message with full context and logging.
        
        Args:
            message_data: Complete webhook message data
            
        Returns:
            Dict with routing decision and metadata
        """
        message_text = message_data.get("body", "")
        phone = message_data.get("from", "")
        
        logger.info(
            "Processing webhook message for routing",
            phone=phone,
            message_length=len(message_text),
            message_id=message_data.get("id", "unknown")
        )
        
        # Perform routing analysis
        routing_result = self.route_message(message_text)
        
        # Add additional context from webhook data
        routing_result.update({
            "phone": phone,
            "message_id": message_data.get("id"),
            "timestamp": message_data.get("timestamp"),
            "user_name": message_data.get("pushName", ""),
            "original_message": message_text
        })
        
        # Log routing decision
        logger.info(
            "Message routing decision",
            phone=phone,
            destination=routing_result["destination"],
            workflow=routing_result["workflow"],
            confidence=routing_result["confidence"],
            priority=routing_result.get("priority", "normal")
        )
        
        return routing_result
    
    def _determine_scheduling_workflow(self, message_text: str) -> str:
        """Determine which specific scheduling workflow to use."""
        if any(word in message_text for word in ["confirmar", "confirmação", "sim", "ok"]):
            return "appointment_confirmation"
        elif any(word in message_text for word in ["reagendar", "remarcar", "mudar", "trocar", "cancelar"]):
            return "appointment_rescheduling"
        elif any(word in message_text for word in ["agendar", "marcar", "consulta", "médico", "horário"]):
            return "appointment_booking"
        else:
            return "appointment_general"  # Default workflow
    
    # MÉTODO REMOVIDO - Sistema independente do N8N
    # Todas as mensagens são processadas internamente por CrewAI
    
    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()