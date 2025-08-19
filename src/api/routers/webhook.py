#!/usr/bin/env python3
"""
Webhook Router - Recepção de mensagens WhatsApp
Processa webhooks da Evolution API e roteia para Hígia Enhanced
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import hashlib
import hmac
import time
import asyncio
from datetime import datetime

from src.core.config import settings
from src.core.logging import get_logger
from src.agents.higia_enhanced import HigiaEnhancedAgent
from src.core.routing.webhook_router import WebhookRouter
from src.clients.evolution_client import EvolutionAPIClient

logger = get_logger(__name__)
router = APIRouter()

# Instâncias globais
higia_agent = None
webhook_router = None
evolution_client = None


async def get_higia_agent():
    """Lazy loading do Hígia Agent"""
    global higia_agent
    if higia_agent is None:
        logger.info("Inicializando Hígia Enhanced Agent...")
        higia_agent = HigiaEnhancedAgent()
        logger.info("✅ Hígia Enhanced Agent inicializado")
    return higia_agent


async def get_webhook_router():
    """Lazy loading do Webhook Router"""
    global webhook_router
    if webhook_router is None:
        logger.info("Inicializando Webhook Router...")
        webhook_router = WebhookRouter()
        logger.info("✅ Webhook Router inicializado")
    return webhook_router


async def get_evolution_client():
    """Lazy loading do Evolution Client"""
    global evolution_client
    if evolution_client is None:
        logger.info("Inicializando Evolution API Client...")
        evolution_client = EvolutionAPIClient()
        logger.info("✅ Evolution API Client inicializado")
    return evolution_client


# Modelos Pydantic para validação
class WebhookMessage(BaseModel):
    """Modelo para mensagens recebidas via webhook"""
    key: Dict[str, Any] = Field(..., description="Chave da mensagem")
    pushName: Optional[str] = Field(None, description="Nome do remetente")
    message: Dict[str, Any] = Field(..., description="Conteúdo da mensagem")
    messageTimestamp: Optional[int] = Field(None, description="Timestamp da mensagem")
    status: Optional[str] = Field(None, description="Status da mensagem")


class WebhookEvent(BaseModel):
    """Modelo para eventos de webhook"""
    event: str = Field(..., description="Tipo de evento")
    instance: str = Field(..., description="Instância da Evolution API")
    data: WebhookMessage = Field(..., description="Dados da mensagem")


class MessageResponse(BaseModel):
    """Modelo para resposta de processamento"""
    success: bool = Field(..., description="Status do processamento")
    message_id: Optional[str] = Field(None, description="ID da mensagem enviada")
    response_text: Optional[str] = Field(None, description="Texto da resposta")
    processing_time: Optional[float] = Field(None, description="Tempo de processamento")
    escalated: Optional[bool] = Field(None, description="Se foi escalado para humano")
    error: Optional[str] = Field(None, description="Erro se houver")


def verify_webhook_signature(request: Request, body: bytes) -> bool:
    """
    Verifica assinatura do webhook para segurança (opcional)
    """
    if not settings.EVOLUTION_API_KEY:
        return True  # Se não há chave configurada, aceita
    
    signature = request.headers.get("x-signature")
    if not signature:
        return True  # Não obrigatório por enquanto
    
    expected = hmac.new(
        settings.EVOLUTION_API_KEY.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)


def extract_message_info(webhook_data: WebhookEvent) -> Dict[str, Any]:
    """
    Extrai informações relevantes da mensagem do webhook
    """
    try:
        data = webhook_data.data
        
        # Extrair número do telefone
        phone = data.key.get("remoteJid", "").replace("@s.whatsapp.net", "")
        
        # Extrair nome
        name = data.pushName or "Cliente"
        
        # Extrair texto da mensagem
        message_content = ""
        message_type = "text"
        
        if "conversation" in data.message:
            message_content = data.message["conversation"]
        elif "extendedTextMessage" in data.message:
            message_content = data.message["extendedTextMessage"].get("text", "")
        elif "audioMessage" in data.message:
            message_type = "audio"
            message_content = "[Mensagem de áudio recebida]"
        elif "imageMessage" in data.message:
            message_type = "image"
            message_content = data.message["imageMessage"].get("caption", "[Imagem recebida]")
        elif "documentMessage" in data.message:
            message_type = "document"
            message_content = "[Documento recebido]"
        else:
            message_content = "[Tipo de mensagem não suportado]"
        
        return {
            "phone": phone,
            "name": name,
            "message": message_content,
            "message_type": message_type,
            "timestamp": data.messageTimestamp or int(time.time()),
            "raw_data": data.dict()
        }
        
    except Exception as e:
        logger.error(f"Erro ao extrair informações da mensagem: {e}")
        return {
            "phone": "unknown",
            "name": "Cliente",
            "message": "Erro ao processar mensagem",
            "message_type": "error",
            "timestamp": int(time.time()),
            "raw_data": {}
        }


async def process_message_async(
    message_info: Dict[str, Any],
    higia: HigiaEnhancedAgent,
    router: WebhookRouter,
    evolution: EvolutionAPIClient
):
    """
    Processa mensagem de forma assíncrona em background
    """
    try:
        start_time = time.time()
        
        logger.info(
            "Processando mensagem",
            phone=message_info["phone"],
            name=message_info["name"],
            message_type=message_info["message_type"]
        )
        
        # 1. Roteamento inteligente
        routing_result = router.route_message(message_info["message"])
        
        logger.info(
            "Roteamento concluído",
            workflow=routing_result["workflow"],
            confidence=routing_result["confidence"],
            priority=routing_result.get("priority", "normal")
        )
        
        # 2. Preparar contexto para Hígia
        context = {
            "message": message_info["message"],
            "phone": message_info["phone"],
            "name": message_info["name"],
            "message_type": message_info["message_type"],
            "routing_result": routing_result,
            "timestamp": message_info["timestamp"]
        }
        
        # 3. Processar com Hígia Enhanced
        result = await higia.process_message(context)
        
        processing_time = time.time() - start_time
        
        logger.info(
            "Processamento Hígia concluído",
            status=result["status"],
            escalate=result.get("escalate", False),
            processing_time=f"{processing_time:.2f}s"
        )
        
        # 4. Enviar resposta via WhatsApp
        if result["status"] == "success" and result.get("response"):
            try:
                send_result = await evolution.send_text_message(
                    to=message_info["phone"],
                    message=result["response"]
                )
                
                if send_result.get("success"):
                    logger.info(
                        "Resposta enviada com sucesso",
                        phone=message_info["phone"],
                        message_id=send_result.get("message_id")
                    )
                else:
                    logger.error(
                        "Erro ao enviar resposta",
                        phone=message_info["phone"],
                        error=send_result.get("error")
                    )
                    
            except Exception as e:
                logger.error(
                    "Erro no envio da resposta",
                    phone=message_info["phone"],
                    error=str(e)
                )
        
        # 5. Log de escalação se necessário
        if result.get("escalate"):
            logger.warning(
                "Mensagem escalada para atendimento humano",
                phone=message_info["phone"],
                reason=routing_result.get("priority", "unknown")
            )
        
        logger.info(
            "Processamento completo finalizado",
            phone=message_info["phone"],
            total_time=f"{processing_time:.2f}s"
        )
        
    except Exception as e:
        logger.error(
            "Erro no processamento assíncrono",
            phone=message_info.get("phone", "unknown"),
            error=str(e),
            exc_info=True
        )


@router.post("/whatsapp", response_model=MessageResponse)
async def receive_whatsapp_webhook(
    webhook_event: WebhookEvent,
    background_tasks: BackgroundTasks,
    request: Request,
    higia: HigiaEnhancedAgent = Depends(get_higia_agent),
    router_instance: WebhookRouter = Depends(get_webhook_router),
    evolution: EvolutionAPIClient = Depends(get_evolution_client)
):
    """
    Endpoint principal para receber webhooks do WhatsApp via Evolution API
    
    Fluxo:
    1. Validar webhook e extrair dados da mensagem
    2. Processar em background para resposta rápida
    3. Rotear mensagem via WebhookRouter
    4. Processar via Hígia Enhanced com MCP
    5. Enviar resposta via Evolution API
    """
    
    try:
        # Log da recepção
        logger.info(
            "Webhook recebido",
            webhook_event_type=webhook_event.event,
            instance=webhook_event.instance,
            timestamp=datetime.now().isoformat()
        )
        
        # Verificar se é evento de mensagem
        if webhook_event.event not in ["messages.upsert", "message.created"]:
            logger.debug(f"Evento ignorado: {webhook_event.event}")
            return MessageResponse(
                success=True,
                message_id=None,
                response_text="Evento ignorado"
            )
        
        # Extrair informações da mensagem
        message_info = extract_message_info(webhook_event)
        
        # Validações básicas
        if not message_info["phone"] or message_info["phone"] == "unknown":
            logger.warning("Mensagem sem telefone válido")
            return MessageResponse(
                success=False,
                error="Telefone não identificado"
            )
        
        if not message_info["message"] or message_info["message_type"] == "error":
            logger.warning("Mensagem sem conteúdo válido")
            return MessageResponse(
                success=False,
                error="Conteúdo da mensagem inválido"
            )
        
        # Processar em background para resposta rápida
        background_tasks.add_task(
            process_message_async,
            message_info,
            higia,
            router_instance,
            evolution
        )
        
        # Resposta imediata para o webhook
        return MessageResponse(
            success=True,
            message_id=None,
            response_text="Mensagem recebida e sendo processada",
            processing_time=0.0,
            escalated=False
        )
        
    except Exception as e:
        logger.error(
            "Erro no processamento do webhook",
            error=str(e),
            webhook_event_type=webhook_event.event,
            exc_info=True
        )
        
        # Retornar erro mas com status 200 para não causar retry
        return MessageResponse(
            success=False,
            error=f"Erro interno: {str(e)}"
        )


@router.get("/test")
async def test_webhook():
    """Endpoint de teste para verificar se o webhook está funcionando"""
    return {
        "status": "ok",
        "message": "Webhook está funcionando",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "higia_agent": higia_agent is not None,
            "webhook_router": webhook_router is not None,
            "evolution_client": evolution_client is not None
        }
    }


@router.post("/test-message")
async def test_message_processing(
    message: str,
    phone: str = "5511999999999",
    name: str = "Teste",
    higia: HigiaEnhancedAgent = Depends(get_higia_agent),
    router_instance: WebhookRouter = Depends(get_webhook_router)
):
    """
    Endpoint para testar processamento de mensagens sem WhatsApp
    """
    try:
        # Simular dados de mensagem
        message_info = {
            "phone": phone,
            "name": name,
            "message": message,
            "message_type": "text",
            "timestamp": int(time.time()),
            "raw_data": {}
        }
        
        # Roteamento
        routing_result = router_instance.route_message(message)
        
        # Contexto
        context = {
            "message": message,
            "phone": phone,
            "name": name,
            "message_type": "text",
            "routing_result": routing_result,
            "timestamp": int(time.time())
        }
        
        # Processar com Hígia
        start_time = time.time()
        result = await higia.process_message(context)
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "routing": routing_result,
            "higia_result": result,
            "processing_time": processing_time,
            "test_mode": True
        }
        
    except Exception as e:
        logger.error(f"Erro no teste de mensagem: {e}")
        raise HTTPException(status_code=500, detail=str(e))