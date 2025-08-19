#!/usr/bin/env python3
"""
Teste Completo do Sistema FastAPI + Hígia Enhanced + MCP
"""

import asyncio
import httpx
import json
import time
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_server_startup():
    """Testa se o servidor inicia sem erros"""
    print("🧪 Testando inicialização do servidor...")
    
    try:
        from src.api.main import app
        print("✅ Aplicação FastAPI carregada com sucesso")
        
        # Verificar routers registrados
        routes = [route.path for route in app.routes]
        expected_routes = [
            "/",
            "/api/v1/webhook/whatsapp", 
            "/api/v1/webhook/test",
            "/api/v1/webhook/test-message",
            "/api/v1/health/",
            "/api/v1/health/quick",
            "/api/v1/health/components/{component}",
            "/api/v1/health/metrics"
        ]
        
        for route in expected_routes:
            if any(r.startswith(route.split("{")[0]) for r in routes):
                print(f"✅ Rota {route} registrada")
            else:
                print(f"⚠️ Rota {route} não encontrada")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_components():
    """Testa componentes individuais"""
    print("\n🧪 Testando componentes individuais...")
    
    # Test Hígia Enhanced
    try:
        from src.agents.higia_enhanced import HigiaEnhancedAgent
        higia = HigiaEnhancedAgent()
        mcp_test = higia.test_mcp_integration()
        
        if all(mcp_test.values()) if isinstance(mcp_test, dict) and all(v for k, v in mcp_test.items() if k != 'errors') else False:
            print("✅ Hígia Enhanced + MCP funcionando")
        else:
            print(f"⚠️ Hígia Enhanced com problemas: {mcp_test}")
            
    except Exception as e:
        print(f"❌ Erro no Hígia Enhanced: {e}")
    
    # Test Evolution Client
    try:
        from src.clients.evolution_client import EvolutionAPIClient
        client = EvolutionAPIClient()
        
        if client._is_configured():
            print("✅ Evolution Client configurado")
        else:
            print("⚠️ Evolution Client não configurado (normal em desenvolvimento)")
            
    except Exception as e:
        print(f"❌ Erro no Evolution Client: {e}")
    
    # Test Webhook Router
    try:
        from src.core.routing.webhook_router import WebhookRouter
        router = WebhookRouter()
        
        test_message = "Preciso agendar consulta para minha filha de 8 anos"
        result = router.route_message(test_message)
        
        if result.get("workflow") == "appointment_booking":
            print("✅ Webhook Router funcionando")
        else:
            print(f"⚠️ Webhook Router com resultado inesperado: {result}")
            
    except Exception as e:
        print(f"❌ Erro no Webhook Router: {e}")


async def test_api_endpoints():
    """Testa endpoints da API sem iniciar servidor"""
    print("\n🧪 Testando processamento de endpoints...")
    
    try:
        from src.api.routers.webhook import test_message_processing
        from src.agents.higia_enhanced import HigiaEnhancedAgent
        from src.core.routing.webhook_router import WebhookRouter
        
        # Instanciar dependências
        higia = HigiaEnhancedAgent()
        router = WebhookRouter()
        
        # Simular request de teste
        test_message = "Olá! Preciso agendar uma consulta psiquiátrica para minha filha de 9 anos."
        phone = "5511999999999"
        name = "Maria Silva"
        
        print(f"🔄 Testando mensagem: '{test_message}'")
        
        # Chamar função diretamente
        result = await test_message_processing(
            message=test_message,
            phone=phone,
            name=name,
            higia=higia,
            router_instance=router
        )
        
        if result.get("success"):
            print("✅ Processamento de mensagem funcionando")
            print(f"   Roteamento: {result['routing']['workflow']}")
            print(f"   Confiança: {result['routing']['confidence']:.2f}")
            print(f"   Status Hígia: {result['higia_result']['status']}")
            print(f"   Tempo: {result['processing_time']:.2f}s")
            
            # Verificar se mencionou Dr. Ernesto (para criança)
            response = result['higia_result'].get('response', '')
            if 'Ernesto' in response or 'ernesto' in response.lower():
                print("✅ Regras especiais aplicadas (Dr. Ernesto para criança)")
            else:
                print("⚠️ Regras especiais podem não ter sido aplicadas")
                
        else:
            print(f"❌ Erro no processamento: {result}")
            
    except Exception as e:
        print(f"❌ Erro no teste de endpoint: {e}")
        import traceback
        traceback.print_exc()


async def test_health_endpoints():
    """Testa endpoints de health check"""
    print("\n🧪 Testando health checks...")
    
    try:
        from src.api.routers.health import health_check, quick_health
        
        # Quick health
        quick_result = await quick_health()
        if quick_result.get("status") == "healthy":
            print("✅ Quick health check OK")
        else:
            print(f"⚠️ Quick health check: {quick_result}")
        
        # Full health check
        health_result = await health_check()
        if health_result.status in ["healthy", "degraded"]:
            print(f"✅ Health check completo: {health_result.status}")
            
            # Detalhes dos componentes
            for component, details in health_result.components.items():
                status = details.get("status", "unknown")
                print(f"   {component}: {status}")
        else:
            print(f"⚠️ Health check com problemas: {health_result.status}")
            
    except Exception as e:
        print(f"❌ Erro no health check: {e}")


async def run_all_tests():
    """Executa todos os testes"""
    print("🚀 TESTE COMPLETO DO SISTEMA FASTAPI - Sistema Vivacità")
    print("=" * 60)
    
    tests = [
        ("Inicialização do Servidor", test_server_startup()),
        ("Componentes Individuais", test_components()),
        ("Endpoints da API", test_api_endpoints()),
        ("Health Checks", test_health_endpoints())
    ]
    
    results = []
    
    for test_name, test_coro in tests:
        print(f"\n📋 {test_name}:")
        try:
            if asyncio.iscoroutine(test_coro):
                result = await test_coro
            else:
                result = test_coro
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro em {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 RESULTADO: {passed}/{total} testes passaram")
    
    if passed >= 3:
        print("\n🎉 SISTEMA FASTAPI PRONTO PARA USO!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Iniciar servidor: poetry run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8181")
        print("2. Acessar docs: http://localhost:8181/docs")
        print("3. Testar webhook: POST http://localhost:8181/api/v1/webhook/test-message")
        print("4. Configurar Evolution API para apontar para seu servidor")
        print("5. Testar com mensagens WhatsApp reais")
        
        print("\n🔧 COMANDOS ÚTEIS:")
        print("# Iniciar servidor")
        print("poetry run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8181")
        print("\n# Testar endpoint direto")
        print('curl -X POST "http://localhost:8181/api/v1/webhook/test-message" \\')
        print('  -H "Content-Type: application/json" \\')
        print('  -d \'{"message": "Olá, preciso de ajuda", "phone": "5511999999999", "name": "Teste"}\'')
        
    else:
        print("\n⚠️ ALGUNS COMPONENTES PRECISAM DE AJUSTES")
        print("🔧 Verifique os erros acima e corrija antes de usar em produção")
    
    return passed >= 3


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)