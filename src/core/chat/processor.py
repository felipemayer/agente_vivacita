"""
Main chat processor using CrewAI for message handling.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from src.core.logging import get_logger
from src.agents.medical_crew import MedicalCrew
from src.integrations.whatsapp.client import WhatsAppClient

logger = get_logger(__name__)


class ChatProcessor:
    """
    Main chat processor that handles messages using CrewAI agents.
    """
    
    def __init__(self):
        """Initialize the chat processor."""
        self.medical_crew = MedicalCrew()
        self.whatsapp_client = WhatsAppClient()
        
    async def process_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming chat message using CrewAI.
        
        Args:
            message_data: Message data from webhook
            
        Returns:
            Processing result with response and metadata
        """
        phone = message_data.get("from", "")
        message_text = message_data.get("body", "")
        message_type = message_data.get("message_type", "text")
        
        logger.info(
            "Processing chat message",
            phone=phone,
            message_type=message_type,
            message_length=len(message_text)
        )
        
        try:
            # Prepare context for CrewAI crew
            context = {
                "message": message_text,
                "phone": phone,
                "message_type": message_type,
                "timestamp": datetime.utcnow().isoformat(),
                "media_url": message_data.get("media_url"),
                "conversation_history": await self._get_conversation_history(phone)
            }
            
            # Process with medical crew
            crew_result = await self.medical_crew.process_consultation(context)
            
            # Send response via WhatsApp
            if crew_result.get("response"):
                await self.whatsapp_client.send_message(
                    phone=phone,
                    message=crew_result["response"]
                )
            
            # Handle escalation if needed
            if crew_result.get("escalate", False):
                await self._handle_escalation(phone, crew_result)
            
            # Log successful processing
            logger.info(
                "Message processed successfully",
                phone=phone,
                response_length=len(crew_result.get("response", "")),
                escalated=crew_result.get("escalate", False)
            )
            
            return {
                "status": "success",
                "response": crew_result.get("response"),
                "escalated": crew_result.get("escalate", False),
                "processing_time": crew_result.get("processing_time", 0),
                "agent_used": crew_result.get("agent_used", "medical_agent")
            }
            
        except Exception as e:
            logger.error(
                "Error processing message",
                phone=phone,
                error=str(e),
                exc_info=True
            )
            
            # Send fallback response
            await self._send_fallback_response(phone)
            
            return {
                "status": "error",
                "error": str(e),
                "fallback_sent": True
            }
    
    async def _get_conversation_history(self, phone: str) -> list:
        """
        Get recent conversation history for context.
        
        Args:
            phone: User phone number
            
        Returns:
            List of recent messages
        """
        # TODO: Implement conversation history retrieval from database
        # This would fetch the last N messages for this phone number
        # to provide context to the CrewAI agents
        
        logger.debug("Getting conversation history", phone=phone)
        
        # Placeholder - implement database query
        return []
    
    async def _handle_escalation(self, phone: str, crew_result: Dict[str, Any]) -> None:
        """
        Handle escalation to human agents.
        
        Args:
            phone: User phone number
            crew_result: Result from crew processing
        """
        logger.info(
            "Handling escalation",
            phone=phone,
            escalation_reason=crew_result.get("escalation_reason", "Unknown")
        )
        
        # TODO: Implement escalation logic
        # - Notify human agents
        # - Transfer conversation context
        # - Set conversation status to "escalated"
        
        # Send escalation message to user
        escalation_message = (
            "Entendo que você precisa de atendimento especializado. "
            "Estou transferindo seu atendimento para um de nossos especialistas. "
            "Aguarde um momento, por favor."
        )
        
        await self.whatsapp_client.send_message(
            phone=phone,
            message=escalation_message
        )
    
    async def _send_fallback_response(self, phone: str) -> None:
        """
        Send fallback response when processing fails.
        
        Args:
            phone: User phone number
        """
        fallback_message = (
            "Desculpe, estou enfrentando algumas dificuldades técnicas no momento. "
            "Por favor, tente novamente em alguns instantes ou entre em contato "
            "com nossa equipe de atendimento."
        )
        
        try:
            await self.whatsapp_client.send_message(
                phone=phone,
                message=fallback_message
            )
        except Exception as e:
            logger.error(
                "Failed to send fallback response",
                phone=phone,
                error=str(e)
            )