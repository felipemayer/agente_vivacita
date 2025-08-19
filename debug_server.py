#!/usr/bin/env python3
"""
Servidor de debug sem middleware de segurança
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import time

from src.core.config import settings
from src.core.logging import get_logger
from src.api.routers import webhook, health
# from src.api.middleware.security import SecurityMiddleware  # REMOVIDO TEMPORARIAMENTE
from src.api.middleware.logging import LoggingMiddleware

logger = get_logger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema Vivacità - DEBUG",
    description="Versão de debug sem security middleware",
    version="1.0.0-debug",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Mais permissivo para debug
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# APENAS Logging Middleware (sem security)
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
    """Endpoint raiz - versão debug"""
    return {
        "service": "Sistema Vivacità - DEBUG MODE",
        "version": "1.0.0-debug",
        "status": "online",
        "environment": "debug",
        "timestamp": time.time(),
        "note": "Security middleware DISABLED for debugging",
        "endpoints": {
            "webhook": "/api/v1/webhook/whatsapp",
            "health": "/api/v1/health",
            "docs": "/docs"
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para debug"""
    logger.error(
        "ERRO DEBUG - Exceção não tratada",
        path=str(request.url.path),
        method=request.method,
        error=str(exc),
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno (debug mode)",
            "message": str(exc),  # Mostra erro real em debug
            "timestamp": time.time(),
            "path": str(request.url.path)
        }
    )

if __name__ == "__main__":
    print("🔧 INICIANDO SERVIDOR DEBUG (sem security middleware)")
    print("Port: 8183")
    print("Logs detalhados habilitados")
    
    uvicorn.run(
        "debug_server:app",
        host="0.0.0.0",
        port=8183,
        reload=False,  # Sem reload para debug mais limpo
        log_level="debug"
    )