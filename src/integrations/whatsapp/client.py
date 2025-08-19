"""
WhatsApp client for Evolution API integration.
"""

import httpx
from typing import Dict, Any, Optional
from datetime import datetime

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class WhatsAppClient:
    """
    Client for sending WhatsApp messages via Evolution API.
    Shared with N8N system.
    """
    
    def __init__(self):
        """Initialize WhatsApp client."""
        self.base_url = settings.EVOLUTION_API_URL.rstrip('/')
        self.api_key = settings.EVOLUTION_API_KEY
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        
    async def send_message(
        self, 
        phone: str, 
        message: str,
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Send a WhatsApp message.
        
        Args:
            phone: Recipient phone number
            message: Message content
            message_type: Type of message (text, image, audio, etc.)
            
        Returns:
            API response
        """
        try:
            # Format phone number (remove any non-digits and ensure format)
            clean_phone = ''.join(filter(str.isdigit, phone))
            if not clean_phone.startswith('55'):
                clean_phone = '55' + clean_phone
            
            payload = {
                "number": clean_phone,
                "text": message,
                "type": message_type
            }
            
            logger.info(
                "Sending WhatsApp message",
                phone=clean_phone,
                message_length=len(message),
                message_type=message_type
            )
            
            response = await self.http_client.post(
                f"{self.base_url}/message/sendText",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(
                    "Message sent successfully",
                    phone=clean_phone,
                    message_id=result.get("id", "unknown")
                )
                return {
                    "success": True,
                    "message_id": result.get("id"),
                    "response": result
                }
            else:
                logger.error(
                    "Failed to send message",
                    phone=clean_phone,
                    status_code=response.status_code,
                    response_text=response.text
                )
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(
                "Error sending WhatsApp message",
                phone=phone,
                error=str(e),
                exc_info=True
            )
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_typing(self, phone: str) -> bool:
        """
        Send typing indicator.
        
        Args:
            phone: Recipient phone number
            
        Returns:
            Success status
        """
        try:
            clean_phone = ''.join(filter(str.isdigit, phone))
            if not clean_phone.startswith('55'):
                clean_phone = '55' + clean_phone
            
            payload = {"number": clean_phone}
            
            response = await self.http_client.post(
                f"{self.base_url}/chat/sendPresence",
                json=payload
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(
                "Error sending typing indicator",
                phone=phone,
                error=str(e)
            )
            return False
    
    async def get_profile_info(self, phone: str) -> Optional[Dict[str, Any]]:
        """
        Get WhatsApp profile information.
        
        Args:
            phone: Phone number to lookup
            
        Returns:
            Profile information or None
        """
        try:
            clean_phone = ''.join(filter(str.isdigit, phone))
            if not clean_phone.startswith('55'):
                clean_phone = '55' + clean_phone
            
            response = await self.http_client.get(
                f"{self.base_url}/chat/fetchProfile/{clean_phone}"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(
                    "Could not fetch profile",
                    phone=clean_phone,
                    status_code=response.status_code
                )
                return None
                
        except Exception as e:
            logger.error(
                "Error fetching profile",
                phone=phone,
                error=str(e)
            )
            return None
    
    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()