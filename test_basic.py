#!/usr/bin/env python3
"""
Teste básico para validar a estrutura do projeto e funcionalidades core
sem dependências externas pesadas.
"""

import os
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_environment_config():
    """Testa se as configurações de ambiente estão corretas."""
    from src.core.config import settings
    
    print("🧪 Testando configurações de ambiente...")
    
    # Verificar se OpenAI API Key está configurada
    assert settings.OPENAI_API_KEY is not None, "OPENAI_API_KEY não configurada"
    assert settings.OPENAI_API_KEY.startswith("sk-"), "OPENAI_API_KEY inválida"
    
    print("✅ OpenAI API Key configurada corretamente")
    
    # Verificar outras configurações básicas
    assert settings.PROJECT_NAME == "Vivacita Chat System"
    assert settings.DEBUG == True
    
    print("✅ Configurações básicas OK")
    return True

def test_webhook_router_basic():
    """Testa o WebhookRouter com mensagens simuladas."""
    from src.core.routing.webhook_router import WebhookRouter
    
    print("\n🧪 Testando WebhookRouter...")
    
    router = WebhookRouter()
    
    # Teste 1: Mensagem de agendamento
    routing_result = router.route_message("Gostaria de agendar uma consulta")
    print(f"📝 Agendamento: {routing_result}")
    
    assert routing_result["destination"] == "crewai"
    assert routing_result["workflow"] in ["appointment_booking", "appointment_general"]
    assert routing_result["confidence"] > 0.5
    
    # Teste 2: Mensagem médica geral
    routing_result = router.route_message("Olá, tenho uma dúvida sobre sintomas")
    print(f"🏥 Consulta médica: {routing_result}")
    
    assert routing_result["destination"] == "crewai"
    assert routing_result["workflow"] == "medical_consultation"
    
    # Teste 3: Emergência
    routing_result = router.route_message("Socorro! Estou passando muito mal")
    print(f"🚨 Emergência: {routing_result}")
    
    assert routing_result["destination"] == "crewai"
    assert routing_result["workflow"] == "emergency_escalation"
    assert routing_result["escalate_immediately"] == True
    assert routing_result["priority"] == "high"
    
    print("✅ WebhookRouter funcionando corretamente")
    return True

def test_medical_tools_basic():
    """Testa as ferramentas médicas básicas."""
    print("\n🧪 Testando ferramentas médicas...")
    
    try:
        from src.tools.medical_tools import base_de_conhecimento
        
        # Teste básico da ferramenta
        result = base_de_conhecimento.invoke("O que é hipertensão?")
        print(f"🔍 Base de conhecimento: {result[:100]}...")
        
        assert isinstance(result, str)
        assert len(result) > 10
        
        print("✅ Ferramentas médicas funcionando")
        return True
    except Exception as e:
        print(f"⚠️ Ferramentas médicas com dependência externa: {e}")
        return False

def test_logging_system():
    """Testa o sistema de logging."""
    print("\n🧪 Testando sistema de logging...")
    
    from src.core.logging import get_logger
    
    logger = get_logger("test")
    
    # Testar diferentes níveis de log
    logger.info("Teste de log INFO")
    logger.warning("Teste de log WARNING")
    logger.error("Teste de log ERROR")
    
    print("✅ Sistema de logging funcionando")
    return True

def main():
    """Executa todos os testes básicos."""
    print("🚀 Iniciando testes básicos do sistema Vivacità...")
    print("=" * 60)
    
    tests = [
        test_environment_config,
        test_webhook_router_basic,
        test_logging_system,
        test_medical_tools_basic,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Erro no teste {test.__name__}: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes básicos passaram!")
        return True
    else:
        print("⚠️ Alguns testes falharam. Verifique as dependências.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)