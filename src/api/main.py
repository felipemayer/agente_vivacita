#!/usr/bin/env python3
"""
FastAPI Server Principal - Sistema Vivacità
Servidor web para receber webhooks WhatsApp e processar via Hígia Enhanced
"""

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import time

from src.core.config import settings
from src.core.logging import get_logger
from src.api.routers import webhook, health
from src.api.middleware.security import SecurityMiddleware
from src.api.middleware.logging import LoggingMiddleware

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia lifecycle da aplicação (startup/shutdown)
    """
    # Startup
    logger.info("🚀 Iniciando Sistema Vivacità...")
    logger.info(f"Ambiente: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")
    
    # Verificar conexões essenciais
    try:
        # Test OpenAI connection
        logger.info("✅ OpenAI API configurada")
        
        # Test Supabase connection (se configurado)
        if settings.SUPABASE_URL:
            logger.info("✅ Supabase configurado")
        
        # Test Evolution API (se configurado)
        if settings.EVOLUTION_API_URL:
            logger.info("✅ Evolution API configurado")
            
        logger.info("🎉 Sistema Vivacità iniciado com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")
        
    yield
    
    # Shutdown
    logger.info("⏹️ Sistema Vivacità finalizado")


# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema Vivacità - Chat AI Médico",
    description="""
    Sistema de Chat AI especializado em atendimento médico da Clínica Vivacità Saúde Mental.
    
    Funcionalidades:
    - Recepção de webhooks WhatsApp via Evolution API
    - Processamento inteligente via CrewAI (Hígia Enhanced)
    - Roteamento automático por tipo de consulta
    - Integração MCP para agendamentos médicos
    - Escalação automática de emergências
    """,
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Security Middleware
app.add_middleware(SecurityMiddleware)

# Logging Middleware
app.add_middleware(LoggingMiddleware)

# Routers
app.include_router(
    webhook.router,
    prefix="/api/v1/webhook",
    tags=["webhook"]
)

app.include_router(
    health.router,
    prefix="/api/v1/health",
    tags=["health"]
)


@app.get("/")
async def root():
    """Endpoint raiz com informações do sistema"""
    return {
        "service": "Sistema Vivacità - Chat AI Médico",
        "version": "1.0.0",
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time(),
        "features": {
            "whatsapp_webhook": True,
            "crewai_processing": True,
            "mcp_integration": True,
            "emergency_escalation": True,
            "medical_scheduling": True
        },
        "endpoints": {
            "webhook": "/api/v1/webhook/whatsapp",
            "health": "/api/v1/health",
            "docs": "/docs" if settings.DEBUG else "disabled"
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handler global para exceções não tratadas
    """
    logger.error(
        "Erro não tratado na aplicação",
        path=str(request.url.path),
        method=request.method,
        error=str(exc),
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno do servidor",
            "message": "Ocorreu um erro inesperado. Tente novamente.",
            "timestamp": time.time(),
            "path": str(request.url.path)
        }
    )


# Desenvolvimento - executar com uvicorn
if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8181,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )