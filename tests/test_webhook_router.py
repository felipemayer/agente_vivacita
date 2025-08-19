"""
Tests for webhook router functionality.
"""

import pytest
from src.core.routing.webhook_router import WebhookRouter


class TestWebhookRouter:
    """Test cases for WebhookRouter."""
    
    def setup_method(self):
        """Setup for each test."""
        self.router = WebhookRouter()
    
    def test_init(self):
        """Test router initialization."""
        assert self.router is not None
        assert hasattr(self.router, 'n8n_patterns')
        assert hasattr(self.router, 'python_chat_patterns')
        assert hasattr(self.router, 'emergency_patterns')
        assert len(self.router.n8n_patterns) > 0
        assert len(self.router.python_chat_patterns) > 0
        assert len(self.router.emergency_patterns) > 0
    
    def test_route_to_n8n_scheduling(self):
        """Test routing scheduling messages to N8N."""
        messages = [
            "Gostaria de agendar uma consulta",
            "Preciso marcar um exame",
            "Quero reagendar minha consulta",
            "Posso confirmar minha consulta?",
            "Confirmo presença para amanhã"
        ]
        
        for message in messages:
            result = self.router.route_message(message)
            assert result["destination"] == "n8n"
            assert result["confidence"] > 0.5
            assert "patterns_matched" in result
            assert result.get("escalate_immediately", False) is False
    
    def test_route_to_python_chat_medical(self):
        """Test routing medical queries to Python Chat."""
        messages = [
            "Quais são os sintomas de gripe?",
            "Como devo me preparar para o exame?",
            "Qual é o horário de funcionamento?",
            "Vocês atendem convênio?",
            "Quais especialidades vocês têm?"
        ]
        
        for message in messages:
            result = self.router.route_message(message)
            assert result["destination"] == "python_chat"
            assert result["confidence"] > 0.5
            assert result.get("escalate_immediately", False) is False
    
    def test_route_ambiguous_message(self):
        """Test routing of ambiguous messages."""
        ambiguous_messages = [
            "Olá",
            "Oi, tudo bem?",
            "Preciso de ajuda",
            "Obrigado"
        ]
        
        for message in ambiguous_messages:
            result = self.router.route_message(message)
            # Should default to python_chat for general inquiries
            assert result["destination"] == "python_chat"
            assert "confidence" in result
            assert result.get("escalate_immediately", False) is False
    
    def test_route_emergency_message(self):
        """Test routing of emergency messages."""
        emergency_messages = [
            "Socorro, estou passando mal!",
            "Emergência médica",
            "Preciso de ajuda urgente",
            "Estou com dor no peito"
        ]
        
        for message in emergency_messages:
            result = self.router.route_message(message)
            assert result["destination"] == "python_chat"
            assert result["priority"] == "high"
            assert result["escalate_immediately"] is True
            assert result["workflow"] == "emergency_escalation"
    
    def test_confidence_scoring(self):
        """Test confidence scoring mechanism."""
        # High confidence N8N routing
        result = self.router.route_message("Gostaria de agendar uma consulta para cardiologia")
        assert result["confidence"] >= 0.8
        
        # High confidence Python Chat routing  
        result = self.router.route_message("Quais são os sintomas de diabetes?")
        assert result["confidence"] >= 0.7
        
        # Lower confidence for ambiguous
        result = self.router.route_message("Olá")
        assert result["confidence"] < 0.7
    
    def test_patterns_matching(self):
        """Test that patterns are correctly identified."""
        result = self.router.route_message("Preciso agendar uma consulta")
        assert "patterns_matched" in result
        assert len(result["patterns_matched"]) > 0
        assert result["destination"] == "n8n"
        
        result = self.router.route_message("Quais são os horários?")
        assert "patterns_matched" in result
        assert result["destination"] == "python_chat"
    
    def test_case_insensitive_routing(self):
        """Test that routing is case insensitive."""
        messages = [
            ("AGENDAR CONSULTA", "n8n"),
            ("agendar consulta", "n8n"),
            ("Agendar Consulta", "n8n"),
            ("HORÁRIO DE FUNCIONAMENTO", "python_chat"),
            ("horário de funcionamento", "python_chat")
        ]
        
        for message, expected_destination in messages:
            result = self.router.route_message(message)
            assert result["destination"] == expected_destination
    
    def test_message_preprocessing(self):
        """Test message preprocessing and cleaning."""
        messages_with_noise = [
            "Olá! Gostaria de agendar uma consulta, por favor.",
            "   agendar consulta   ",
            "Agendar... consulta?",
            "AGENDAR!!! CONSULTA!!!"
        ]
        
        for message in messages_with_noise:
            result = self.router.route_message(message)
            assert result["destination"] == "n8n"
            assert result["confidence"] > 0.5