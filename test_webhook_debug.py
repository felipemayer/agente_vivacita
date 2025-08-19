#!/usr/bin/env python3
"""
Script de debug para testar webhook sem middleware
"""

import asyncio
import httpx
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_webhook_direct():
    """Testa webhook diretamente"""
    print("🧪 Testando webhook Evolution API...")
    
    # Dados de teste simulando Evolution API real
    webhook_data = {
        "event": "messages.upsert",
        "instance": "vivacita-test",
        "data": {
            "key": {
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": False,
                "id": "TEST_MESSAGE_123"
            },
            "message": {
                "conversation": "Olá! Preciso agendar uma consulta para minha filha de 8 anos"
            },
            "messageTimestamp": 1692123456,
            "pushName": "Maria Silva Teste"
        }
    }
    
    # Headers como Evolution API enviaria
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Evolution-API/1.0",
        "X-Forwarded-For": "127.0.0.1"
    }
    
    print(f"📤 Enviando para: http://localhost:8182/api/v1/webhook/whatsapp")
    print(f"📋 Dados: {json.dumps(webhook_data, indent=2, ensure_ascii=False)}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8182/api/v1/webhook/whatsapp",
                json=webhook_data,
                headers=headers
            )
            
            print(f"📨 Status: {response.status_code}")
            print(f"📋 Headers: {dict(response.headers)}")
            
            try:
                response_data = response.json()
                print(f"📄 Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"📄 Response (raw): {response.text}")
                
            if response.status_code == 200:
                print("✅ Webhook funcionando!")
                return True
            else:
                print(f"❌ Erro: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

async def test_simple_endpoint():
    """Testa endpoint simples primeiro"""
    print("\n🧪 Testando endpoint simples...")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://localhost:8182/")
            
            print(f"📨 Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Servidor online: {data['service']}")
                return True
            else:
                print(f"❌ Erro: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

async def main():
    print("🚀 TESTE DE DEBUG - Webhook Evolution API")
    print("=" * 50)
    
    # Teste 1: Endpoint simples
    simple_ok = await test_simple_endpoint()
    if not simple_ok:
        print("❌ Servidor não está acessível")
        return
    
    # Teste 2: Webhook
    webhook_ok = await test_webhook_direct()
    
    if webhook_ok:
        print("\n🎉 Webhook está funcionando!")
    else:
        print("\n⚠️ Problema no webhook - verifique logs do servidor")

if __name__ == "__main__":
    asyncio.run(main())