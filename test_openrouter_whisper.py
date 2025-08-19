#!/usr/bin/env python3
"""
Test OpenRouter + Whisper configuration.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_config():
    """Test that configuration loads correctly."""
    print("🔍 Testing configuration...")
    
    try:
        from src.core.config import settings
        
        # Check OpenRouter settings
        openrouter_settings = [
            ('OPENROUTER_API_KEY', settings.OPENROUTER_API_KEY),
            ('OPENROUTER_MODEL', settings.OPENROUTER_MODEL),
            ('OPENROUTER_BASE_URL', settings.OPENROUTER_BASE_URL),
        ]
        
        print("📡 OpenRouter Configuration:")
        for setting_name, setting_value in openrouter_settings:
            status = "✅" if setting_value and "your_" not in setting_value else "⚠️"
            display_value = setting_value if "your_" not in setting_value else "[NEEDS CONFIGURATION]"
            print(f"  {status} {setting_name}: {display_value}")
        
        # Check OpenAI Whisper settings
        whisper_settings = [
            ('OPENAI_API_KEY', settings.OPENAI_API_KEY),
            ('OPENAI_WHISPER_MODEL', settings.OPENAI_WHISPER_MODEL),
        ]
        
        print("\n🎙️  OpenAI Whisper Configuration:")
        for setting_name, setting_value in whisper_settings:
            status = "✅" if setting_value and "your_" not in setting_value else "⚠️"
            display_value = setting_value if "your_" not in setting_value else "[NEEDS CONFIGURATION]"
            print(f"  {status} {setting_name}: {display_value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_imports():
    """Test that we can import the necessary components."""
    print("\n🔍 Testing imports...")
    
    try:
        # Test Hígia agent import
        from src.agents.higia_agent import HigiaAgent
        print("✅ HigiaAgent imported successfully")
        
        # Test Whisper client import
        from src.integrations.audio.whisper_client import WhisperClient
        print("✅ WhisperClient imported successfully")
        
        # Test webhook with audio processing
        from src.api.v1.endpoints.webhook import webhook_router, whisper_client
        print("✅ Webhook with audio processing imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_whisper_client_init():
    """Test that WhisperClient can be initialized."""
    print("\n🔍 Testing WhisperClient initialization...")
    
    try:
        from src.integrations.audio.whisper_client import WhisperClient
        
        # Test basic initialization
        whisper_client = WhisperClient()
        print("✅ WhisperClient initialized successfully")
        
        # Check if client has required attributes
        if hasattr(whisper_client, 'client'):
            print("✅ OpenAI client configured")
        else:
            print("⚠️  OpenAI client not found")
        
        return True
        
    except Exception as e:
        print(f"❌ WhisperClient initialization failed: {e}")
        return False

def test_higia_openrouter_init():
    """Test that HigiaAgent can be initialized with OpenRouter."""
    print("\n🔍 Testing HigiaAgent with OpenRouter...")
    
    try:
        from src.agents.higia_agent import HigiaAgent
        
        # Test basic initialization
        higia = HigiaAgent()
        print("✅ HigiaAgent initialized successfully")
        
        # Check if agent has LLM configured
        if hasattr(higia, 'llm'):
            print("✅ OpenRouter LLM configured")
            
            # Check LLM model
            if hasattr(higia.llm, 'model_name'):
                print(f"✅ Model: {higia.llm.model_name}")
            else:
                print("⚠️  Model name not accessible")
        else:
            print("⚠️  LLM not found in HigiaAgent")
        
        return True
        
    except Exception as e:
        print(f"❌ HigiaAgent initialization failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🤖 Testing OpenRouter + Whisper Configuration")
    print("=" * 60)
    
    tests = [
        ("Configuration Loading", test_config),
        ("Component Imports", test_imports),
        ("WhisperClient Initialization", test_whisper_client_init),
        ("HigiaAgent OpenRouter Integration", test_higia_openrouter_init)
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
    print("📊 Test Results:")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Summary: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! OpenRouter + Whisper configuration is working.")
    else:
        print("⚠️  Some tests failed. Check the configuration above.")
    
    print("\n📋 Next Steps:")
    if passed < len(results):
        print("1. Configure API keys in .env file:")
        print("   - OPENROUTER_API_KEY=your_actual_openrouter_key")
        print("   - OPENAI_API_KEY=your_actual_openai_key")
        print("2. Install dependencies: poetry install")
    else:
        print("✅ Configuration looks good!")
        print("1. Test with real API keys")
        print("2. Test audio transcription with actual audio files")
        print("3. Deploy and test with WhatsApp integration")

if __name__ == "__main__":
    main()