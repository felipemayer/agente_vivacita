#!/usr/bin/env python3
"""
Security Middleware - Middleware de segurança para FastAPI
Rate limiting, validação de requests e proteções básicas
"""

import time
import hashlib
from typing import Dict, Optional
from collections import defaultdict, deque
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import ipaddress

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """
    Rate limiter baseado em IP e endpoint
    """
    
    def __init__(self):
        # Armazenar requests por IP
        self.requests: Dict[str, deque] = defaultdict(lambda: deque())
        
        # Configurações de rate limiting
        self.limits = {
            "/api/v1/webhook/whatsapp": {"count": 60, "window": 60},  # 60 req/min
            "/api/v1/webhook/test-message": {"count": 10, "window": 60},  # 10 req/min  
            "default": {"count": 100, "window": 60}  # 100 req/min para outros
        }
    
    def is_allowed(self, ip: str, endpoint: str) -> bool:
        """
        Verifica se request está dentro do limite
        """
        current_time = time.time()
        
        # Obter configuração para o endpoint
        config = self.limits.get(endpoint, self.limits["default"])
        window = config["window"]
        max_count = config["count"]
        
        # Limpar requests antigas
        requests_queue = self.requests[ip]
        while requests_queue and current_time - requests_queue[0] > window:
            requests_queue.popleft()
        
        # Verificar limite
        if len(requests_queue) >= max_count:
            return False
        
        # Adicionar nova request
        requests_queue.append(current_time)
        return True
    
    def get_reset_time(self, ip: str) -> float:
        """
        Retorna quando o rate limit será resetado
        """
        requests_queue = self.requests[ip]
        if not requests_queue:
            return 0
        
        oldest_request = requests_queue[0]
        return oldest_request + 60  # 60 segundos de janela


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware de segurança com rate limiting e validações
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.rate_limiter = RateLimiter()
        
        # IPs bloqueados (pode ser expandido para incluir DB/Redis)
        self.blocked_ips = set()
        
        # IPs permitidos (whitelist para webhooks)
        self.allowed_ips = set()
        if hasattr(settings, 'ALLOWED_WEBHOOK_IPS'):
            self.allowed_ips.update(settings.ALLOWED_WEBHOOK_IPS)
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extrai IP real do cliente considerando proxies
        """
        # Headers de proxy comuns
        forwarded_headers = [
            "x-forwarded-for",
            "x-real-ip",
            "cf-connecting-ip",  # Cloudflare
            "x-forwarded"
        ]
        
        for header in forwarded_headers:
            if header in request.headers:
                ip = request.headers[header].split(",")[0].strip()
                try:
                    # Validar se é um IP válido
                    ipaddress.ip_address(ip)
                    return ip
                except ValueError:
                    continue
        
        # Fallback para IP direto
        return request.client.host if request.client else "unknown"
    
    def _is_webhook_endpoint(self, path: str) -> bool:
        """
        Verifica se é endpoint de webhook
        """
        webhook_paths = [
            "/api/v1/webhook/whatsapp",
            "/api/v1/webhook/test"
        ]
        return any(path.startswith(wp) for wp in webhook_paths)
    
    def _validate_request_size(self, request: Request) -> bool:
        """
        Valida tamanho do request
        """
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                # Limite de 10MB para requests
                return size <= 10 * 1024 * 1024
            except ValueError:
                return False
        return True
    
    def _validate_content_type(self, request: Request) -> bool:
        """
        Valida content-type para endpoints específicos
        """
        if request.method == "POST":
            content_type = request.headers.get("content-type", "")
            
            # Endpoints que esperam JSON
            if "/api/v1/webhook/" in request.url.path:
                return content_type.startswith("application/json")
        
        return True
    
    async def dispatch(self, request: Request, call_next):
        """
        Processa request através das validações de segurança
        """
        start_time = time.time()
        
        try:
            # Extrair informações do request
            client_ip = self._get_client_ip(request)
            path = request.url.path
            method = request.method
            
            # Log de request
            logger.debug(
                "Security middleware - request received",
                ip=client_ip,
                path=path,
                method=method,
                user_agent=request.headers.get("user-agent", "unknown")
            )
            
            # 1. Verificar IP bloqueado
            if client_ip in self.blocked_ips:
                logger.warning(f"Request de IP bloqueado: {client_ip}")
                return JSONResponse(
                    status_code=403,
                    content={"error": "IP bloqueado"}
                )
            
            # 2. Rate limiting
            if not self.rate_limiter.is_allowed(client_ip, path):
                reset_time = self.rate_limiter.get_reset_time(client_ip)
                logger.warning(
                    "Rate limit excedido",
                    ip=client_ip,
                    path=path,
                    reset_time=reset_time
                )
                
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit excedido",
                        "reset_time": reset_time
                    },
                    headers={
                        "Retry-After": "60",
                        "X-RateLimit-Limit": "60",
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(reset_time))
                    }
                )
            
            # 3. Validar tamanho do request
            if not self._validate_request_size(request):
                logger.warning(f"Request muito grande de {client_ip}")
                return JSONResponse(
                    status_code=413,
                    content={"error": "Request muito grande"}
                )
            
            # 4. Validar content-type
            if not self._validate_content_type(request):
                logger.warning(f"Content-type inválido de {client_ip}")
                return JSONResponse(
                    status_code=415,
                    content={"error": "Content-Type não suportado"}
                )
            
            # 5. Headers de segurança básicos
            if method == "OPTIONS":
                # Resposta para preflight CORS
                response = Response()
                response.headers["Access-Control-Allow-Origin"] = "*"
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
                response.headers["Access-Control-Allow-Headers"] = "*"
                return response
            
            # Processar request
            response = await call_next(request)
            
            # Adicionar headers de segurança
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            
            # Log de resposta
            processing_time = time.time() - start_time
            logger.debug(
                "Security middleware - response sent",
                ip=client_ip,
                path=path,
                status=response.status_code,
                processing_time=f"{processing_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "Erro no security middleware",
                error=str(e),
                path=request.url.path,
                exc_info=True
            )
            
            return JSONResponse(
                status_code=500,
                content={"error": "Erro interno de segurança"}
            )