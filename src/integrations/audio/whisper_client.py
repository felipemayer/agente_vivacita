"""
OpenAI Whisper client for audio transcription.
"""

import openai
from typing import Optional
import httpx
import tempfile
import os

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class WhisperClient:
    """
    Client for OpenAI Whisper API to transcribe audio messages.
    """
    
    def __init__(self):
        """Initialize Whisper client with OpenAI API key."""
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
    async def transcribe_audio_url(self, audio_url: str) -> Optional[str]:
        """
        Transcribe audio from URL using Whisper.
        
        Args:
            audio_url: URL of the audio file to transcribe
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            logger.info("Starting audio transcription", url=audio_url)
            
            # Download audio file
            audio_data = await self._download_audio(audio_url)
            if not audio_data:
                return None
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Transcribe using Whisper
                with open(temp_file_path, 'rb') as audio_file:
                    transcript = self.client.audio.transcriptions.create(
                        model=settings.OPENAI_WHISPER_MODEL,
                        file=audio_file,
                        language="pt"  # Portuguese
                    )
                
                transcribed_text = transcript.text
                
                logger.info(
                    "Audio transcription successful",
                    text_length=len(transcribed_text),
                    preview=transcribed_text[:50] + "..." if len(transcribed_text) > 50 else transcribed_text
                )
                
                return transcribed_text
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(
                "Error transcribing audio",
                url=audio_url,
                error=str(e),
                exc_info=True
            )
            return None
    
    async def _download_audio(self, url: str) -> Optional[bytes]:
        """
        Download audio file from URL.
        
        Args:
            url: Audio file URL
            
        Returns:
            Audio file bytes or None if failed
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
                response.raise_for_status()
                
                logger.info(
                    "Audio download successful",
                    url=url,
                    size_bytes=len(response.content),
                    content_type=response.headers.get("content-type", "unknown")
                )
                
                return response.content
                
        except Exception as e:
            logger.error(
                "Error downloading audio",
                url=url,
                error=str(e),
                exc_info=True
            )
            return None
    
    def transcribe_audio_file(self, file_path: str) -> Optional[str]:
        """
        Transcribe audio from local file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            logger.info("Transcribing local audio file", path=file_path)
            
            with open(file_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=settings.OPENAI_WHISPER_MODEL,
                    file=audio_file,
                    language="pt"  # Portuguese
                )
            
            transcribed_text = transcript.text
            
            logger.info(
                "Local audio transcription successful",
                text_length=len(transcribed_text),
                preview=transcribed_text[:50] + "..." if len(transcribed_text) > 50 else transcribed_text
            )
            
            return transcribed_text
            
        except Exception as e:
            logger.error(
                "Error transcribing local audio file",
                path=file_path,
                error=str(e),
                exc_info=True
            )
            return None