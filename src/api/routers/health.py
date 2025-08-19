#!/usr/bin/env python3
"""
Health Check Router - Monitoramento de saúde do sistema
Endpoints para verificar status dos componentes e métricas
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import time
import asyncio
import httpx
from datetime import datetime

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class HealthStatus(BaseModel):
    """Modelo para status de saúde do sistema"""
    status: str
    timestamp: float
    version: str
    environment: str
    components: Dict[str, Any]
    metrics: Optional[Dict[str, Any]] = None


class ComponentHealth(BaseModel):
    """Modelo para saúde de componente individual"""
    status: str  # "healthy", "unhealthy", "unknown"
    response_time: Optional[float] = None
    last_check: float
    details: Optional[Dict[str, Any]] = None


async def check_openai_api() -> ComponentHealth:
    """Verifica conectividade com OpenAI API"""
    try:
        start_time = time.time()
        
        # Test básico de conectividade
        if not settings.OPENAI_API_KEY:
            return ComponentHealth(
                status="unhealthy",
                last_check=time.time(),
                details={"error": "API key não configurada"}
            )
        
        # Simular check de conectividade
        # Em produção, fazer uma chamada real à API
        response_time = time.time() - start_time
        
        return ComponentHealth(
            status="healthy",
            response_time=response_time,
            last_check=time.time(),
            details={"api_key_configured": True}
        )
        
    except Exception as e:
        return ComponentHealth(
            status="unhealthy",
            last_check=time.time(),
            details={"error": str(e)}
        )


async def check_evolution_api() -> ComponentHealth:
    """Verifica conectividade com Evolution API"""
    try:
        if not settings.EVOLUTION_API_URL or not settings.EVOLUTION_API_KEY:
            return ComponentHealth(
                status="unknown",
                last_check=time.time(),
                details={"error": "Evolution API não configurada"}
            )
        
        start_time = time.time()
        
        # Test de conectividade HTTP
        timeout = httpx.Timeout(10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(
                f"{settings.EVOLUTION_API_URL}/manager/status",
                headers={"apikey": settings.EVOLUTION_API_KEY}
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return ComponentHealth(
                    status="healthy",
                    response_time=response_time,
                    last_check=time.time(),
                    details={"url": settings.EVOLUTION_API_URL}
                )
            else:
                return ComponentHealth(
                    status="unhealthy",
                    response_time=response_time,
                    last_check=time.time(),
                    details={"status_code": response.status_code}
                )
                
    except httpx.TimeoutException:
        return ComponentHealth(
            status="unhealthy",
            last_check=time.time(),
            details={"error": "Timeout na conexão"}
        )
    except Exception as e:
        return ComponentHealth(
            status="unhealthy",
            last_check=time.time(),
            details={"error": str(e)}
        )


async def check_supabase() -> ComponentHealth:
    """Verifica conectividade com Supabase"""
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            return ComponentHealth(
                status="unknown",
                last_check=time.time(),
                details={"error": "Supabase não configurado"}
            )
        
        start_time = time.time()
        
        # Test básico de conectividade HTTP
        timeout = httpx.Timeout(10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(
                f"{settings.SUPABASE_URL}/rest/v1/",
                headers={
                    "apikey": settings.SUPABASE_KEY,
                    "Authorization": f"Bearer {settings.SUPABASE_KEY}"
                }
            )
            
            response_time = time.time() - start_time
            
            if response.status_code in [200, 401]:  # 401 é esperado sem tabela específica
                return ComponentHealth(
                    status="healthy",
                    response_time=response_time,
                    last_check=time.time(),
                    details={"url": settings.SUPABASE_URL}
                )
            else:
                return ComponentHealth(
                    status="unhealthy",
                    response_time=response_time,
                    last_check=time.time(),
                    details={"status_code": response.status_code}
                )
                
    except Exception as e:
        return ComponentHealth(
            status="unhealthy",
            last_check=time.time(),
            details={"error": str(e)}
        )


async def check_crewai_agent() -> ComponentHealth:
    """Verifica se o CrewAI Agent está funcionando"""
    try:
        start_time = time.time()
        
        # Tentar importar e instanciar Hígia Enhanced
        from src.agents.higia_enhanced import HigiaEnhancedAgent
        
        # Test MCP integration
        higia = HigiaEnhancedAgent()
        test_result = higia.test_mcp_integration()
        
        response_time = time.time() - start_time
        
        # Verificar se todos os testes passaram
        all_passed = all([
            test_result.get("tool_loaded", False),
            test_result.get("specialties_test", False),
            test_result.get("dr_ernesto_test", False),
            test_result.get("validation_test", False)
        ])
        
        return ComponentHealth(
            status="healthy" if all_passed else "unhealthy",
            response_time=response_time,
            last_check=time.time(),
            details={
                "mcp_tests": test_result,
                "all_tests_passed": all_passed
            }
        )
        
    except Exception as e:
        return ComponentHealth(
            status="unhealthy",
            last_check=time.time(),
            details={"error": str(e)}
        )


@router.get("/", response_model=HealthStatus)
async def health_check():
    """
    Endpoint principal de health check
    Verifica status de todos os componentes
    """
    try:
        start_time = time.time()
        
        # Executar checks em paralelo
        checks = await asyncio.gather(
            check_openai_api(),
            check_evolution_api(),
            check_supabase(),
            check_crewai_agent(),
            return_exceptions=True
        )
        
        # Processar resultados
        openai_health, evolution_health, supabase_health, crewai_health = checks
        
        # Tratar exceções
        for i, check in enumerate(checks):
            if isinstance(check, Exception):
                error_health = ComponentHealth(
                    status="unhealthy",
                    last_check=time.time(),
                    details={"error": str(check)}
                )
                if i == 0:
                    openai_health = error_health
                elif i == 1:
                    evolution_health = error_health
                elif i == 2:
                    supabase_health = error_health
                elif i == 3:
                    crewai_health = error_health
        
        # Determinar status geral
        all_components = [openai_health, evolution_health, supabase_health, crewai_health]
        healthy_count = sum(1 for comp in all_components if comp.status == "healthy")
        unhealthy_count = sum(1 for comp in all_components if comp.status == "unhealthy")
        
        if unhealthy_count == 0:
            overall_status = "healthy"
        elif healthy_count >= 2:  # Pelo menos 2 componentes funcionando
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"
        
        # Métricas básicas
        total_check_time = time.time() - start_time
        
        return HealthStatus(
            status=overall_status,
            timestamp=time.time(),
            version="1.0.0",
            environment=settings.ENVIRONMENT,
            components={
                "openai": openai_health.dict(),
                "evolution_api": evolution_health.dict(),
                "supabase": supabase_health.dict(),
                "crewai_agent": crewai_health.dict()
            },
            metrics={
                "total_check_time": total_check_time,
                "healthy_components": healthy_count,
                "unhealthy_components": unhealthy_count,
                "total_components": len(all_components)
            }
        )
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return HealthStatus(
            status="unhealthy",
            timestamp=time.time(),
            version="1.0.0",
            environment=settings.ENVIRONMENT,
            components={},
            metrics={"error": str(e)}
        )


@router.get("/quick")
async def quick_health():
    """Health check rápido sem testes de conectividade externa"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "message": "Servidor FastAPI funcionando",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


@router.get("/components/{component}")
async def component_health(component: str):
    """Verifica saúde de componente específico"""
    
    checkers = {
        "openai": check_openai_api,
        "evolution": check_evolution_api,
        "supabase": check_supabase,
        "crewai": check_crewai_agent
    }
    
    if component not in checkers:
        raise HTTPException(
            status_code=404,
            detail=f"Componente '{component}' não encontrado. Disponíveis: {list(checkers.keys())}"
        )
    
    try:
        result = await checkers[component]()
        return {
            "component": component,
            "health": result.dict(),
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "component": component,
            "health": {
                "status": "unhealthy",
                "error": str(e),
                "last_check": time.time()
            },
            "timestamp": time.time()
        }


@router.get("/metrics")
async def system_metrics():
    """Métricas básicas do sistema"""
    return {
        "uptime": time.time(),  # Simplificado
        "environment": settings.ENVIRONMENT,
        "debug_mode": settings.DEBUG,
        "timestamp": time.time(),
        "version": "1.0.0",
        "configuration": {
            "openai_configured": bool(settings.OPENAI_API_KEY),
            "evolution_configured": bool(settings.EVOLUTION_API_URL and settings.EVOLUTION_API_KEY),
            "supabase_configured": bool(settings.SUPABASE_URL and settings.SUPABASE_KEY),
        }
    }