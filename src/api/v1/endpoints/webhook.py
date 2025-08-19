"""
Webhook endpoints for WhatsApp message processing.
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

from src.core.logging import get_logger
from src.core.routing.webhook_router import WebhookRouter
from src.core.chat.processor import ChatProcessor
from src.integrations.audio.whisper_client import WhisperClient

logger = get_logger(__name__)
router = APIRouter()

# Initialize components
webhook_router = WebhookRouter()
chat_processor = ChatProcessor()
whisper_client = WhisperClient()


class WebhookMessage(BaseModel):
    """WhatsApp webhook message model."""
    body: str
    from_: Optional[str] = None
    phone: Optional[str] = None
    id: Optional[str] = None
    timestamp: Optional[str] = None
    message_type: Optional[str] = "text"
    media_url: Optional[str] = None
    pushName: Optional[str] = None
    
    class Config:
        fields = {"from_": "from"}


class WebhookResponse(BaseModel):
    """Webhook response model."""
    status: str
    message: str
    route_decision: str
    processed_by: str
    timestamp: datetime


@router.post("/whatsapp", response_model=WebhookResponse)
async def whatsapp_webhook(
    message: WebhookMessage,
    background_tasks: BackgroundTasks
) -> WebhookResponse:
    """
    Process incoming WhatsApp messages via Evolution API webhook.
    
    This endpoint:
    1. Receives webhook from Evolution API
    2. Routes message to Python Chat or N8N based on content analysis
    3. Processes chat messages using CrewAI system
    4. Returns immediate response while processing in background
    """
    logger.info(
        "Webhook received",
        phone=message.from_ or message.phone,
        message_preview=message.body[:50] + "..." if len(message.body) > 50 else message.body,
        message_type=message.message_type
    )
    
    try:
        # Process audio messages with Whisper if needed
        message_body = message.body
        if message.message_type == "audio" and message.media_url:
            logger.info("Processing audio message with Whisper", media_url=message.media_url)
            transcribed_text = await whisper_client.transcribe_audio_url(message.media_url)
            if transcribed_text:
                message_body = f"[Áudio transcrito]: {transcribed_text}"
                logger.info("Audio transcription successful", text_preview=transcribed_text[:50])
            else:
                message_body = "[Áudio recebido - não foi possível transcrever]"
                logger.warning("Audio transcription failed")
        
        # Convert message to dict for processing
        message_data = {
            "body": message_body,
            "from": message.from_ or message.phone,
            "id": message.id,
            "timestamp": message.timestamp,
            "message_type": message.message_type,
            "media_url": message.media_url,
            "pushName": message.pushName,
            "original_body": message.body  # Keep original for reference
        }
        
        # Step 1: Intelligent routing decision with full context
        route_decision = await webhook_router.route_webhook_message(message_data)
        
        # SISTEMA INDEPENDENTE: Todas as mensagens são processadas por CrewAI
        logger.info(
            "Routing to CrewAI System",
            phone=route_decision.get("phone"),
            agent=route_decision.get("agent"),
            workflow=route_decision.get("workflow"),
            confidence=route_decision.get("confidence"),
            priority=route_decision.get("priority"),
            escalate_immediately=route_decision.get("escalate_immediately", False)
        )
        
        # Process in background to avoid webhook timeout
        background_tasks.add_task(
            chat_processor.process_message,
            {**message_data, "routing_result": route_decision}
        )
        
        return WebhookResponse(
            status="accepted",
            message=f"Message routed to {route_decision.get('agent', 'CrewAI')} - {route_decision['workflow']}",
            route_decision="crewai",
            processed_by=f"{route_decision.get('agent', 'crewai')}_{route_decision['workflow']}",
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(
            "Webhook processing failed",
            error=str(e),
            phone=message.from_ or message.phone,
            exc_info=True
        )
        
        # In case of error, try to process with basic CrewAI fallback
        try:
            fallback_route = {
                "destination": "crewai",
                "workflow": "error_fallback", 
                "agent": "medical_agent",
                "confidence": 0.5,
                "phone": message.from_ or message.phone,
                "message_id": message.id,
                "original_message": message.body,
                "reason": "Error fallback routing - processing with basic medical agent"
            }
            
            background_tasks.add_task(
                chat_processor.process_message,
                {**{"body": message.body, "from": message.from_ or message.phone}, "routing_result": fallback_route}
            )
            
            return WebhookResponse(
                status="error_fallback",
                message="Error occurred, message processing with CrewAI fallback",
                route_decision="crewai_fallback",
                processed_by="medical_agent_fallback",
                timestamp=datetime.utcnow()
            )
        except Exception as fallback_error:
            logger.error(
                "Fallback also failed",
                error=str(fallback_error),
                original_error=str(e),
                exc_info=True
            )
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process webhook message"
            )


@router.get("/test")
async def test_webhook() -> Dict[str, Any]:
    """
    Test endpoint for webhook functionality.
    """
    return {
        "message": "Webhook endpoint is working",
        "routes": {
            "whatsapp": "/api/v1/webhook/whatsapp",
            "test": "/api/v1/webhook/test"
        },
        "status": "ready"
    }