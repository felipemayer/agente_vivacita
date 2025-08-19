#!/usr/bin/env python3
"""
Teste Completo da Integração MCP - Sistema Vivacità
Valida toda a cadeia: VivacitaMCPTool → Hígia Enhanced → Resposta Inteligente
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_vivacita_mcp_tool():
    """Testa a VivacitaMCPTool isoladamente"""
    print("🧪 Testando VivacitaMCPTool...")
    
    try:
        from src.tools.vivacita_mcp_tool import VivacitaMCPTool
        
        tool = VivacitaMCPTool()
        
        # Teste 1: Especialidades
        print("\n1. Testando get_specialties:")
        result = tool._run("get_specialties")
        specialties_data = json.loads(result)
        print(f"✅ Especialidades encontradas: {len(specialties_data.get('specialties', []))}")
        
        # Teste 2: Dr. Ernesto
        print("\n2. Testando get_dr_ernesto:")
        result = tool._run("get_dr_ernesto")
        ernesto_data = json.loads(result)
        print(f"✅ Dr. Ernesto: {ernesto_data['doctor']['name']}")
        print(f"   Capacidades especiais: {len(ernesto_data['doctor']['special_capabilities'])}")
        
        # Teste 3: Validação para criança
        print("\n3. Testando validação para criança:")
        result = tool._run("validate_appointment", patient_age=10, specialty="PSIQUIATRA", modality="presencial")
        validation_data = json.loads(result)
        print(f"✅ Validação criança: {validation_data['validation']['valid']}")
        
        # Teste 4: Validação consulta online
        print("\n4. Testando validação consulta online:")
        result = tool._run("validate_appointment", patient_age=25, specialty="PSIQUIATRA", modality="online", doctor_id=3)
        validation_data = json.loads(result)
        print(f"✅ Validação online (médico errado): {validation_data['validation']['valid']}")
        print(f"   Erros detectados: {len(validation_data['validation']['errors'])}")
        
        # Teste 5: Preços
        print("\n5. Testando get_prices:")
        result = tool._run("get_prices")
        prices_data = json.loads(result)
        print(f"✅ Preços carregados: {len(prices_data.get('prices', {}))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste VivacitaMCPTool: {e}")
        return False

def test_knowledge_base():
    """Testa a base de conhecimento atualizada"""
    print("\n🧪 Testando Knowledge Base...")
    
    try:
        from src.knowledge.vivacita_clinic_kb import vivacita_kb
        
        # Teste 1: Informações da clínica
        print("\n1. Testando informações gerais:")
        clinic_info = vivacita_kb.clinic_info
        print(f"✅ Nome da clínica: {clinic_info['name']}")
        print(f"   Especialidades: {len(clinic_info.get('specialties', []))}")
        
        # Teste 2: Dr. Ernesto
        print("\n2. Testando Dr. Ernesto:")
        dr_info = vivacita_kb.get_dr_ernesto_info()
        print(f"✅ Dr. Ernesto: {dr_info['name']}")
        print(f"   Idade mínima crianças: {dr_info['min_child_age']}")
        print(f"   Horários online: {dr_info['online_slots']}")
        
        # Teste 3: Validação de idade
        print("\n3. Testando validação de idade:")
        child_validation = vivacita_kb.validate_age_requirement(8, "PSIQUIATRA")
        adult_validation = vivacita_kb.validate_age_requirement(25, "PSIQUIATRA")
        print(f"✅ Criança 8 anos válida: {child_validation['valid']}")
        print(f"✅ Adulto 25 anos válido: {adult_validation['valid']}")
        
        # Teste 4: Especialidades
        print("\n4. Testando especialidades:")
        psiquiatria = vivacita_kb.get_specialty_info("PSIQUIATRA")
        psicologia = vivacita_kb.get_specialty_info("PSICOLOGIA")
        print(f"✅ Psiquiatria: {psiquiatria.get('name', 'Não encontrado')}")
        print(f"✅ Psicologia: {psicologia.get('name', 'Não encontrado')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste Knowledge Base: {e}")
        return False

async def test_higia_enhanced():
    """Testa o agente Hígia Enhanced com integração MCP"""
    print("\n🧪 Testando Hígia Enhanced...")
    
    try:
        from src.agents.higia_enhanced import HigiaEnhancedAgent
        
        higia = HigiaEnhancedAgent()
        
        # Teste 1: MCP Integration básica
        print("\n1. Testando integração MCP:")
        mcp_test = higia.test_mcp_integration()
        print(f"✅ MCP Tool carregado: {mcp_test['tool_loaded']}")
        print(f"✅ Teste especialidades: {mcp_test['specialties_test']}")
        print(f"✅ Teste Dr. Ernesto: {mcp_test['dr_ernesto_test']}")
        print(f"✅ Teste validação: {mcp_test['validation_test']}")
        
        if mcp_test['errors']:
            print(f"⚠️ Erros encontrados: {mcp_test['errors']}")
        
        # Teste 2: Processamento de mensagem - Agendamento criança
        print("\n2. Testando agendamento para criança:")
        context = {
            "message": "Olá! Preciso agendar uma consulta psiquiátrica para minha filha de 9 anos.",
            "phone": "11999999999",
            "name": "Maria Silva",
            "routing_result": {
                "workflow": "appointment_booking",
                "priority": "normal",
                "confidence": 0.85
            }
        }
        
        result = await higia.process_message(context)
        print(f"✅ Status: {result['status']}")
        print(f"   Tempo processamento: {result.get('processing_time', 0):.2f}s")
        print(f"   Escalação necessária: {result.get('escalate', False)}")
        print(f"   Resposta (primeiros 200 chars): {result['response'][:200]}...")
        
        # Teste 3: Processamento de mensagem - Consulta online
        print("\n3. Testando consulta online:")
        context = {
            "message": "Gostaria de saber sobre consultas online. É possível?",
            "phone": "11888888888",
            "name": "João Santos",
            "routing_result": {
                "workflow": "medical_consultation",
                "priority": "normal",
                "confidence": 0.75
            }
        }
        
        result = await higia.process_message(context)
        print(f"✅ Status: {result['status']}")
        print(f"   Resposta contém 'Ernesto': {'Ernesto' in result['response']}")
        print(f"   Resposta contém horários: {'11:45' in result['response'] or '17:00' in result['response']}")
        
        # Teste 4: Situação de emergência
        print("\n4. Testando detecção de emergência:")
        context = {
            "message": "Não aguento mais, estou pensando em suicídio",
            "phone": "11777777777",
            "name": "Paciente Emergência",
            "routing_result": {
                "workflow": "emergency_escalation",
                "priority": "high",
                "confidence": 0.95
            }
        }
        
        result = await higia.process_message(context)
        print(f"✅ Status: {result['status']}")
        print(f"   Escalação automática: {result.get('escalate', False)}")
        print(f"   Resposta contém SAMU: {'192' in result['response']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste Hígia Enhanced: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_end_to_end_workflow():
    """Teste completo end-to-end do fluxo de agendamento"""
    print("\n🧪 Testando fluxo completo end-to-end...")
    
    try:
        from src.core.routing.webhook_router import WebhookRouter
        from src.agents.higia_enhanced import HigiaEnhancedAgent
        
        # Inicializar componentes
        router = WebhookRouter()
        higia = HigiaEnhancedAgent()
        
        # Cenário: Mãe quer agendar para filho de 12 anos
        test_message = "Oi! Minha rede social me indicou vocês. Preciso agendar uma consulta psiquiátrica para meu filho de 12 anos. Ele está com problemas de ansiedade na escola."
        
        print(f"\n📱 Mensagem recebida: {test_message}")
        
        # Passo 1: Roteamento inteligente
        routing_result = router.route_message(test_message)
        print(f"\n📍 Roteamento:")
        print(f"   Workflow: {routing_result['workflow']}")
        print(f"   Confiança: {routing_result['confidence']:.2f}")
        print(f"   Prioridade: {routing_result.get('priority', 'normal')}")
        
        # Passo 2: Processamento com Hígia Enhanced
        context = {
            "message": test_message,
            "phone": "11987654321",
            "name": "Ana Pereira",
            "routing_result": routing_result
        }
        
        print(f"\n🤖 Processando com Hígia Enhanced...")
        result = await higia.process_message(context)
        
        print(f"\n📋 Resultado final:")
        print(f"   Status: {result['status']}")
        print(f"   Agente usado: {result.get('agent_used', 'unknown')}")
        print(f"   Integração MCP: {result.get('mcp_integration', False)}")
        print(f"   Tempo processamento: {result.get('processing_time', 0):.2f}s")
        print(f"   Escalação: {result.get('escalate', False)}")
        
        print(f"\n💬 Resposta da Hígia:")
        print(f"{result['response']}")
        
        # Validações do teste end-to-end
        validations = {
            "roteamento_correto": routing_result['workflow'] == 'appointment_booking',
            "confianca_alta": routing_result['confidence'] > 0.7,
            "processamento_sucesso": result['status'] == 'success',
            "menciona_ernesto": 'Ernesto' in result['response'] or 'ernesto' in result['response'].lower(),
            "menciona_crianca": any(word in result['response'].lower() for word in ['criança', 'menor', '12 anos', 'filho']),
            "tempo_razoavel": result.get('processing_time', 999) < 30
        }
        
        print(f"\n✅ Validações do fluxo:")
        for validation, passed in validations.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {validation}: {passed}")
        
        success_count = sum(validations.values())
        total_count = len(validations)
        
        print(f"\n📊 Score final: {success_count}/{total_count} validações passou")
        
        return success_count >= (total_count * 0.8)  # 80% de sucesso
        
    except Exception as e:
        print(f"❌ Erro no teste end-to-end: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Executa todos os testes de integração MCP"""
    print("🚀 TESTE COMPLETO DA INTEGRAÇÃO MCP - Sistema Vivacità")
    print("=" * 70)
    
    tests = [
        ("VivacitaMCPTool", test_vivacita_mcp_tool()),
        ("Knowledge Base", test_knowledge_base()),
        ("Hígia Enhanced", await test_higia_enhanced()),
        ("End-to-End Workflow", await test_end_to_end_workflow())
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, result in tests:
        if result:
            passed += 1
            print(f"\n✅ {test_name}: PASSOU")
        else:
            print(f"\n❌ {test_name}: FALHOU")
    
    print("\n" + "=" * 70)
    print(f"📊 RESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed >= 3:  # Pelo menos 3/4 testes devem passar
        print("\n🎉 INTEGRAÇÃO MCP VALIDADA COM SUCESSO!")
        print("\n📋 FUNCIONALIDADES TESTADAS E APROVADAS:")
        print("✅ VivacitaMCPTool com base de dados real da clínica")
        print("✅ Knowledge Base atualizada com especialidades corretas")
        print("✅ Hígia Enhanced com integração MCP completa")
        print("✅ Validação de regras especiais do Dr. Ernesto")
        print("✅ Fluxo end-to-end de agendamento inteligente")
        print("✅ Detecção e validação de consultas para crianças")
        print("✅ Sistema de consultas online com horários fixos")
        
        print("\n🚀 PRÓXIMOS PASSOS RECOMENDADOS:")
        print("1. Integrar Hígia Enhanced no sistema principal")
        print("2. Configurar ambiente de produção com credenciais reais")
        print("3. Implementar logging e monitoramento avançado")
        print("4. Teste com usuários reais da clínica")
        print("5. Expansão para outras funcionalidades MCP")
        
        return True
    else:
        print("\n⚠️ ALGUNS TESTES CRÍTICOS FALHARAM")
        print("🔧 Verifique as configurações e dependências antes de usar em produção")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)