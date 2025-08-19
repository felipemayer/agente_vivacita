#!/usr/bin/env python3
"""
Evolution API Client - Cliente para envio de mensagens WhatsApp
Integração com Evolution API para enviar mensagens, áudios e documentos
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class MessageType(Enum):
    """Tipos de mensagem suportados"""
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"
    BUTTON = "button"
    LIST = "list"


@dataclass
class SendResult:
    """Resultado do envio de mensagem"""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    response_time: Optional[float] = None
    retry_count: int = 0


class EvolutionAPIClient:
    """
    Cliente para Evolution API WhatsApp
    
    Funcionalidades:
    - Envio de mensagens de texto
    - Envio de áudios
    - Envio de imagens com caption
    - Envio de documentos
    - Retry automático com backoff
    - Rate limiting
    - Logging estruturado
    """
    
    def __init__(self):
        self.base_url = settings.EVOLUTION_API_URL
        self.api_key = settings.EVOLUTION_API_KEY
        self.instance_name = settings.EVOLUTION_API_INSTANCE
        
        # Configurações
        self.timeout = httpx.Timeout(30.0)
        self.max_retries = 3
        self.retry_delay = 1.0  # segundos
        self.rate_limit = 10  # mensagens por minuto
        
        # Rate limiting
        self._last_requests = []
        
        # Validar configuração
        if not self.base_url or not self.api_key:
            logger.warning("Evolution API não configurada completamente")
    
    def _is_configured(self) -> bool:
        """Verifica se a API está configurada"""
        return bool(self.base_url and self.api_key)
    
    def _clean_phone_number(self, phone: str) -> str:
        """
        Limpa e formata número de telefone
        """
        # Remove todos os caracteres não numéricos
        clean = ''.join(filter(str.isdigit, phone))
        
        # Garantir que tem código do país (Brasil = 55)
        if len(clean) == 11 and clean.startswith('1'):
            clean = '55' + clean
        elif len(clean) == 10:
            clean = '5511' + clean
        elif len(clean) == 11 and not clean.startswith('55'):
            clean = '55' + clean
            
        return clean + '@s.whatsapp.net'
    
    def _check_rate_limit(self):
        """
        Verifica e aplica rate limiting
        """
        current_time = time.time()
        
        # Limpar requests antigas (mais de 1 minuto)
        self._last_requests = [
            req_time for req_time in self._last_requests
            if current_time - req_time < 60
        ]
        
        # Verificar limite
        if len(self._last_requests) >= self.rate_limit:
            sleep_time = 60 - (current_time - self._last_requests[0])
            if sleep_time > 0:
                logger.warning(f"Rate limit atingido, aguardando {sleep_time:.1f}s")
                time.sleep(sleep_time)
        
        # Registrar nova request
        self._last_requests.append(current_time)
    
    async def _make_request(
        self, 
        endpoint: str, 
        data: Dict[str, Any], 
        retry_count: int = 0
    ) -> SendResult:
        """
        Faz requisição HTTP para Evolution API com retry
        """
        if not self._is_configured():
            return SendResult(
                success=False,
                error="Evolution API não configurada"
            )
        
        url = f"{self.base_url}/message/{endpoint}"
        headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
        
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=data
                )
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    
                    return SendResult(
                        success=True,
                        message_id=result.get("message", {}).get("key", {}).get("id"),
                        response_time=response_time,
                        retry_count=retry_count
                    )
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    
                    # Retry em casos específicos
                    if response.status_code >= 500 and retry_count < self.max_retries:
                        logger.warning(
                            f"Erro de servidor, tentativa {retry_count + 1}/{self.max_retries}",
                            status_code=response.status_code
                        )
                        
                        await asyncio.sleep(self.retry_delay * (2 ** retry_count))
                        return await self._make_request(endpoint, data, retry_count + 1)
                    
                    return SendResult(
                        success=False,
                        error=error_msg,
                        response_time=response_time,
                        retry_count=retry_count
                    )
                    
        except httpx.TimeoutException:
            error_msg = "Timeout na requisição"
            
            if retry_count < self.max_retries:
                logger.warning(
                    f"Timeout, tentativa {retry_count + 1}/{self.max_retries}"
                )
                await asyncio.sleep(self.retry_delay * (2 ** retry_count))
                return await self._make_request(endpoint, data, retry_count + 1)
            
            return SendResult(
                success=False,
                error=error_msg,
                retry_count=retry_count
            )
            
        except Exception as e:
            return SendResult(
                success=False,
                error=str(e),
                retry_count=retry_count
            )
    
    async def send_text_message(
        self, 
        to: str, 
        message: str,
        delay: Optional[int] = None
    ) -> SendResult:
        """
        Envia mensagem de texto simples
        
        Args:
            to: Número do telefone (será formatado automaticamente)
            message: Texto da mensagem
            delay: Delay em milissegundos (opcional)
        """
        if not message.strip():
            return SendResult(
                success=False,
                error="Mensagem vazia"
            )
        
        # Rate limiting
        self._check_rate_limit()
        
        # Preparar dados
        formatted_phone = self._clean_phone_number(to)
        data = {
            "number": formatted_phone,
            "text": message.strip()
        }
        
        if delay:
            data["delay"] = delay
        
        logger.info(
            "Enviando mensagem de texto",
            to=to,
            formatted_phone=formatted_phone,
            message_length=len(message)
        )
        
        result = await self._make_request("sendText/" + self.instance_name, data)
        
        if result.success:
            logger.info(
                "Mensagem enviada com sucesso",
                to=to,
                message_id=result.message_id,
                response_time=f"{result.response_time:.2f}s"
            )
        else:
            logger.error(
                "Erro ao enviar mensagem",
                to=to,
                error=result.error,
                retries=result.retry_count
            )
        
        return result
    
    async def send_audio_message(
        self,
        to: str,
        audio_url: str,
        delay: Optional[int] = None
    ) -> SendResult:
        """
        Envia mensagem de áudio
        
        Args:
            to: Número do telefone
            audio_url: URL do arquivo de áudio
            delay: Delay em milissegundos (opcional)
        """
        formatted_phone = self._clean_phone_number(to)
        data = {
            "number": formatted_phone,
            "audioMessage": {
                "audio": audio_url
            }
        }
        
        if delay:
            data["delay"] = delay
        
        logger.info(
            "Enviando mensagem de áudio",
            to=to,
            audio_url=audio_url
        )
        
        result = await self._make_request("sendWhatsAppAudio/" + self.instance_name, data)
        
        if result.success:
            logger.info(
                "Áudio enviado com sucesso",
                to=to,
                message_id=result.message_id
            )
        else:
            logger.error(
                "Erro ao enviar áudio",
                to=to,
                error=result.error
            )
        
        return result
    
    async def send_image_message(
        self,
        to: str,
        image_url: str,
        caption: Optional[str] = None,
        delay: Optional[int] = None
    ) -> SendResult:
        """
        Envia mensagem de imagem com caption opcional
        """
        formatted_phone = self._clean_phone_number(to)
        data = {
            "number": formatted_phone,
            "mediaMessage": {
                "mediatype": "image",
                "media": image_url
            }
        }
        
        if caption:
            data["mediaMessage"]["caption"] = caption
            
        if delay:
            data["delay"] = delay
        
        logger.info(
            "Enviando mensagem de imagem",
            to=to,
            image_url=image_url,
            has_caption=bool(caption)
        )
        
        result = await self._make_request("sendMedia/" + self.instance_name, data)
        
        if result.success:
            logger.info(
                "Imagem enviada com sucesso",
                to=to,
                message_id=result.message_id
            )
        else:
            logger.error(
                "Erro ao enviar imagem",
                to=to,
                error=result.error
            )
        
        return result
    
    async def send_document_message(
        self,
        to: str,
        document_url: str,
        filename: str,
        delay: Optional[int] = None
    ) -> SendResult:
        """
        Envia documento
        """
        formatted_phone = self._clean_phone_number(to)
        data = {
            "number": formatted_phone,
            "mediaMessage": {
                "mediatype": "document",
                "media": document_url,
                "filename": filename
            }
        }
        
        if delay:
            data["delay"] = delay
        
        logger.info(
            "Enviando documento",
            to=to,
            filename=filename
        )
        
        result = await self._make_request("sendMedia/" + self.instance_name, data)
        
        if result.success:
            logger.info(
                "Documento enviado com sucesso",
                to=to,
                message_id=result.message_id
            )
        else:
            logger.error(
                "Erro ao enviar documento",
                to=to,
                error=result.error
            )
        
        return result
    
    async def get_instance_status(self) -> Dict[str, Any]:
        """
        Verifica status da instância
        """
        if not self._is_configured():
            return {
                "status": "not_configured",
                "error": "Evolution API não configurada"
            }
        
        try:
            url = f"{self.base_url}/instance/connectionState/{self.instance_name}"
            headers = {"apikey": self.api_key}
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    return {
                        "status": "ok",
                        "data": response.json(),
                        "instance": self.instance_name
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"HTTP {response.status_code}",
                        "instance": self.instance_name
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "instance": self.instance_name
            }
    
    async def test_connection(self) -> bool:
        """
        Testa conectividade básica com a API
        """
        try:
            status = await self.get_instance_status()
            return status.get("status") == "ok"
        except:
            return False


# Instância global para reutilização
_evolution_client = None


def get_evolution_client() -> EvolutionAPIClient:
    """
    Retorna instância global do Evolution API Client
    """
    global _evolution_client
    if _evolution_client is None:
        _evolution_client = EvolutionAPIClient()
    return _evolution_client


# Para testes diretos
if __name__ == "__main__":
    async def test_client():
        client = EvolutionAPIClient()
        
        print("🧪 Testando Evolution API Client...")
        
        # Test de configuração
        print(f"Configurado: {client._is_configured()}")
        
        if client._is_configured():
            # Test de status
            status = await client.get_instance_status()
            print(f"Status da instância: {status}")
            
            # Test de conectividade
            connected = await client.test_connection()
            print(f"Conectividade: {connected}")
            
            # Test de envio (descomente para testar com número real)
            # result = await client.send_text_message(
            #     "5511999999999", 
            #     "Teste do Sistema Vivacità - Mensagem automática"
            # )
            # print(f"Resultado envio: {result}")
    
    import asyncio
    asyncio.run(test_client())