"""
Medical crew configuration with CrewAI agents.
Updated to use unified Hígia agent following original prompt specifications.
"""

from typing import Dict, Any
from datetime import datetime
import time

from src.core.logging import get_logger
from src.agents.higia_agent import HigiaAgent

logger = get_logger(__name__)


class MedicalCrew:
    """
    Unified Hígia agent system following original prompt specifications.
    Replaces multiple agents with single Hígia agent for consistency.
    """
    
    def __init__(self):
        """Initialize with unified Hígia agent."""
        # Use unified Hígia agent
        self.higia_agent = HigiaAgent()
        
        logger.info("Medical crew initialized with Hígia agent successfully")
    
    async def process_consultation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process consultation using unified Hígia agent.
        
        Args:
            context: Consultation context with message and metadata
            
        Returns:
            Processing result with response and escalation decision
        """
        start_time = time.time()
        
        message = context.get("message", "")
        phone = context.get("phone", "")
        
        logger.info(
            "Starting Hígia consultation processing",
            phone=phone,
            message_preview=message[:50]
        )
        
        try:
            # Process message using unified Hígia agent
            result = await self.higia_agent.process_message(context)
            
            processing_time = time.time() - start_time
            
            logger.info(
                "Hígia consultation processed",
                phone=phone,
                processing_time=processing_time,
                escalated=result.get("escalate", False),
                response_length=len(result.get("response", ""))
            )
            
            return {
                "response": result.get("response", ""),
                "escalate": result.get("escalate", False),
                "escalation_reason": "Hígia determined escalation needed" if result.get("escalate") else "",
                "processing_time": processing_time,
                "agent_used": "higia",
                "workflow": result.get("workflow", "general"),
                "priority": result.get("priority", "normal")
            }
            
        except Exception as e:
            logger.error(
                "Error in Hígia processing",
                phone=phone,
                error=str(e),
                exc_info=True
            )
            
            # Fallback response using Hígia's fallback
            processing_time = time.time() - start_time
            return {
                "response": self.higia_agent._get_fallback_response(),
                "escalate": True,
                "escalation_reason": f"Technical error in Hígia processing: {str(e)}",
                "processing_time": processing_time,
                "agent_used": "higia_fallback"
            }