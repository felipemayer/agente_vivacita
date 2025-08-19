#!/usr/bin/env python3
"""
Logging Middleware - Middleware para logging estruturado de requests
"""

import time
import json
import uuid
from typing import Any, Dict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.logging import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logging estruturado de requests/responses
    """
    
    def __init__(self, app):
        super().__init__(app)
        
        # Paths que não devem ser logados (para evitar spam)
        self.skip_paths = {
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/favicon.ico"
        }
        
        # Paths sensíveis onde não devemos logar o body
        self.sensitive_paths = {
            "/api/v1/webhook/whatsapp"
        }
    
    def _should_log_request(self, path: str) -> bool:
        """
        Determina se deve logar o request
        """
        return not any(path.startswith(skip) for skip in self.skip_paths)
    
    def _should_log_body(self, path: str) -> bool:
        """
        Determina se deve logar o body do request
        """
        return not any(path.startswith(sensitive) for sensitive in self.sensitive_paths)
    
    def _extract_request_info(self, request: Request) -> Dict[str, Any]:
        """
        Extrai informações relevantes do request
        """
        # Headers importantes (sem dados sensíveis)
        important_headers = {
            "user-agent": request.headers.get("user-agent"),
            "content-type": request.headers.get("content-type"),
            "content-length": request.headers.get("content-length"),
            "x-forwarded-for": request.headers.get("x-forwarded-for"),
            "x-real-ip": request.headers.get("x-real-ip")
        }
        
        # Filtrar headers vazios
        headers = {k: v for k, v in important_headers.items() if v is not None}
        
        return {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": headers,
            "client_ip": request.client.host if request.client else None
        }
    
    async def _read_request_body(self, request: Request) -> str:
        """
        Lê body do request de forma segura
        """
        try:
            body = await request.body()
            if body:
                # Tentar decodificar como JSON para logging limpo
                try:
                    json_body = json.loads(body.decode('utf-8'))
                    return json.dumps(json_body, indent=2, ensure_ascii=False)
                except:
                    # Se não for JSON válido, retornar como string
                    return body.decode('utf-8', errors='replace')[:1000]  # Limitar tamanho
            return ""
        except Exception as e:
            logger.warning(f"Erro ao ler body do request: {e}")
            return "[Erro ao ler body]"
    
    def _extract_response_info(self, response: Response) -> Dict[str, Any]:
        """
        Extrai informações relevantes da response
        """
        return {
            "status_code": response.status_code,
            "headers": {
                "content-type": response.headers.get("content-type"),
                "content-length": response.headers.get("content-length")
            }
        }
    
    async def dispatch(self, request: Request, call_next):
        """
        Processa request com logging estruturado
        """
        # Gerar ID único para o request
        request_id = str(uuid.uuid4())[:8]
        
        # Verificar se deve logar
        if not self._should_log_request(request.url.path):
            return await call_next(request)
        
        start_time = time.time()
        
        # Informações do request
        request_info = self._extract_request_info(request)
        
        # Log do request recebido
        logger.info(
            "Request recebido",
            request_id=request_id,
            **request_info
        )
        
        # Log do body se apropriado
        if (request.method in ["POST", "PUT", "PATCH"] and 
            self._should_log_body(request.url.path)):
            
            body = await self._read_request_body(request)
            if body:
                logger.debug(
                    "Request body",
                    request_id=request_id,
                    body=body
                )
        
        try:
            # Processar request
            response = await call_next(request)
            
            # Calcular tempo de processamento
            processing_time = time.time() - start_time
            
            # Informações da response
            response_info = self._extract_response_info(response)
            
            # Log da response
            log_level = "info"
            if response.status_code >= 400:
                log_level = "warning" if response.status_code < 500 else "error"
            
            getattr(logger, log_level)(
                "Request processado",
                request_id=request_id,
                processing_time=f"{processing_time:.3f}s",
                **response_info
            )
            
            # Adicionar request ID no header da response
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Log de erro
            processing_time = time.time() - start_time
            
            logger.error(
                "Erro no processamento do request",
                request_id=request_id,
                processing_time=f"{processing_time:.3f}s",
                error=str(e),
                exc_info=True
            )
            
            # Re-raise para que seja tratado pelo exception handler
            raise