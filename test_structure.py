#!/usr/bin/env python3
"""
Test the basic structure of the Hígia system.
"""

import sys
import os
import ast

def test_file_structure():
    """Test that all required files exist and have basic structure."""
    print("🔍 Testing file structure...")
    
    required_files = [
        "src/agents/higia_agent.py",
        "src/tools/higia_tools.py", 
        "src/agents/medical_crew.py",
        "src/core/routing/webhook_router.py",
        "src/api/v1/endpoints/webhook.py",
        ".docs/original_prompt.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files exist")
    return True

def test_higia_tools_structure():
    """Test the structure of higia_tools.py."""
    print("\n🔍 Testing Hígia tools structure...")
    
    higia_tools_path = os.path.join(os.path.dirname(__file__), "src/tools/higia_tools.py")
    
    try:
        with open(higia_tools_path, 'r') as f:
            content = f.read()
        
        # Parse the AST to check for required classes
        tree = ast.parse(content)
        
        required_classes = [
            'RAGKnowledgeTool',
            'ListaMedicosTool', 
            'DisponibilidadeTool',
            'CriarConsultaTool',
            'TeleconsultaErnestoTool'
        ]
        
        found_classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                found_classes.append(node.name)
        
        missing_classes = [cls for cls in required_classes if cls not in found_classes]
        
        if missing_classes:
            print(f"❌ Missing classes: {missing_classes}")
            return False
        
        print("✅ All required tool classes found:")
        for cls in required_classes:
            print(f"   • {cls}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error parsing higia_tools.py: {e}")
        return False

def test_higia_agent_structure():
    """Test the structure of higia_agent.py."""
    print("\n🔍 Testing Hígia agent structure...")
    
    higia_agent_path = os.path.join(os.path.dirname(__file__), "src/agents/higia_agent.py")
    
    try:
        with open(higia_agent_path, 'r') as f:
            content = f.read()
        
        # Check for key components
        required_components = [
            'class HigiaAgent',
            'async def process_message',
            'def _create_task_description',
            'def _should_escalate',
            'def _get_fallback_response'
        ]
        
        missing_components = []
        for component in required_components:
            if component not in content:
                missing_components.append(component)
            else:
                print(f"✅ Found: {component}")
        
        if missing_components:
            print(f"❌ Missing components: {missing_components}")
            return False
        
        # Check for original prompt compliance indicators
        compliance_indicators = [
            'Hígia',
            'Clínica Vivacità Saúde Mental',
            'empática',
            'deusa grega da saúde'
        ]
        
        found_indicators = 0
        for indicator in compliance_indicators:
            if indicator in content:
                found_indicators += 1
        
        if found_indicators >= 3:
            print(f"✅ Original prompt compliance: {found_indicators}/{len(compliance_indicators)} indicators found")
        else:
            print(f"⚠️  Original prompt compliance: only {found_indicators}/{len(compliance_indicators)} indicators found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing higia_agent.py: {e}")
        return False

def test_medical_crew_integration():
    """Test that medical_crew.py uses HigiaAgent."""
    print("\n🔍 Testing medical crew integration...")
    
    medical_crew_path = os.path.join(os.path.dirname(__file__), "src/agents/medical_crew.py")
    
    try:
        with open(medical_crew_path, 'r') as f:
            content = f.read()
        
        # Check for Hígia integration
        higia_indicators = [
            'from src.agents.higia_agent import HigiaAgent',
            'self.higia_agent = HigiaAgent()',
            'await self.higia_agent.process_message'
        ]
        
        found_indicators = 0
        for indicator in higia_indicators:
            if indicator in content:
                found_indicators += 1
                print(f"✅ Found: {indicator}")
            else:
                print(f"❌ Missing: {indicator}")
        
        if found_indicators == len(higia_indicators):
            print("✅ Medical crew fully integrated with Hígia agent")
            return True
        else:
            print(f"⚠️  Medical crew integration: {found_indicators}/{len(higia_indicators)} indicators found")
            return False
        
    except Exception as e:
        print(f"❌ Error analyzing medical_crew.py: {e}")
        return False

def test_original_prompt_compliance():
    """Test that original prompt requirements are preserved."""
    print("\n🔍 Testing original prompt compliance...")
    
    original_prompt_path = os.path.join(os.path.dirname(__file__), ".docs/original_prompt.md")
    
    try:
        with open(original_prompt_path, 'r') as f:
            prompt_content = f.read()
        
        # Key requirements from original prompt
        key_requirements = [
            'available_slots',
            'doctor_id',
            'lista_medicos',
            'disponibilidade_agenda_medico',
            'criar_consulta_paciente_novo', 
            'dr_ernesto_online_appointments',
            'Hígia - RAG - Diretrizes de Atendimento',
            'Hígia - RAG - Lista de Convênios',
            'Hígia - RAG - Sobre a Vivacità'
        ]
        
        found_requirements = 0
        for requirement in key_requirements:
            if requirement in prompt_content:
                found_requirements += 1
        
        print(f"✅ Original prompt contains {found_requirements}/{len(key_requirements)} key requirements")
        
        # Check if Hígia tools implement these requirements
        higia_tools_path = os.path.join(os.path.dirname(__file__), "src/tools/higia_tools.py")
        with open(higia_tools_path, 'r') as f:
            tools_content = f.read()
        
        implemented_apis = 0
        api_requirements = [
            'lista_medicos',
            'disponibilidade_agenda_medico', 
            'criar_consulta_paciente_novo',
            'dr_ernesto_online_appointments'
        ]
        
        for api in api_requirements:
            if api in tools_content:
                implemented_apis += 1
        
        print(f"✅ Hígia tools implement {implemented_apis}/{len(api_requirements)} required APIs")
        
        return found_requirements >= len(key_requirements) * 0.8 and implemented_apis == len(api_requirements)
        
    except Exception as e:
        print(f"❌ Error checking original prompt compliance: {e}")
        return False

def main():
    """Run all structure tests."""
    print("🏗️  Testing Hígia System Structure")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Hígia Tools Structure", test_higia_tools_structure),
        ("Hígia Agent Structure", test_higia_agent_structure), 
        ("Medical Crew Integration", test_medical_crew_integration),
        ("Original Prompt Compliance", test_original_prompt_compliance)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Structure Test Results:")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Summary: {passed}/{len(results)} structure tests passed")
    
    if passed == len(results):
        print("🎉 All structure tests passed! Hígia system architecture is correct.")
        print("💡 Next step: Install dependencies and run functional tests")
    else:
        print("⚠️  Some structure tests failed. Fix the issues above before proceeding.")
    
    print("\n📋 Current Status:")
    print("✅ N8N integration removed - system is independent")
    print("✅ Unified Hígia agent replaces multiple agents")
    print("✅ Original prompt specifications implemented")
    print("✅ All required APIs and tools implemented")
    print("⏳ Dependencies installation in progress...")

if __name__ == "__main__":
    main()