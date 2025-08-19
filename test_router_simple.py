#!/usr/bin/env python3
"""
Simple test script for webhook router without pytest dependencies.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.routing.webhook_router import WebhookRouter

def test_router_basic():
    """Test basic router functionality."""
    router = WebhookRouter()
    
    # Test N8N routing
    result = router.route_message("Gostaria de agendar uma consulta")
    print(f"Scheduling message result: {result}")
    assert result["destination"] == "n8n"
    assert result["confidence"] > 0.6
    assert result["workflow"] == "agendamento"
    
    # Test Python Chat routing
    result = router.route_message("Quais são os horários de funcionamento?")
    print(f"Info message result: {result}")
    assert result["destination"] == "python_chat"
    assert result["confidence"] > 0.5
    
    # Test emergency routing
    result = router.route_message("Socorro! Estou passando mal!")
    print(f"Emergency message result: {result}")
    assert result["destination"] == "python_chat"
    assert result["priority"] == "high"
    assert result["escalate_immediately"] is True
    assert result["workflow"] == "emergency_escalation"
    
    print("✅ All basic router tests passed!")

def test_message_normalization():
    """Test message normalization."""
    router = WebhookRouter()
    
    # Test case insensitive
    result1 = router.route_message("AGENDAR CONSULTA")
    result2 = router.route_message("agendar consulta")
    assert result1["destination"] == result2["destination"] == "n8n"
    
    # Test text variations
    result = router.route_message("vc tem horário disponível?")
    print(f"Normalized message result: {result}")
    # Should normalize "vc" to "você"
    
    print("✅ Message normalization tests passed!")

def test_pattern_matching():
    """Test pattern matching."""
    router = WebhookRouter()
    
    # Test N8N patterns
    n8n_messages = [
        "Confirmo minha consulta de amanhã",
        "Preciso remarcar para outro dia", 
        "Cancelar consulta",
        "Marcar exame"
    ]
    
    for msg in n8n_messages:
        result = router.route_message(msg)
        print(f"N8N pattern '{msg}': {result['destination']} ({result['confidence']:.2f})")
        assert result["destination"] == "n8n"
    
    # Test Python Chat patterns
    chat_messages = [
        "Como devo me preparar para o exame?",
        "Quais sintomas de gripe?",
        "Vocês atendem convênio Unimed?",
        "Onde fica a clínica?"
    ]
    
    for msg in chat_messages:
        result = router.route_message(msg)
        print(f"Chat pattern '{msg}': {result['destination']} ({result['confidence']:.2f})")
        assert result["destination"] == "python_chat"
    
    print("✅ Pattern matching tests passed!")

if __name__ == "__main__":
    print("🧪 Testing Webhook Router...")
    
    try:
        test_router_basic()
        test_message_normalization()
        test_pattern_matching()
        
        print("\n🎉 All webhook router tests passed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)