"""
Test configuration and fixtures.
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Async test client for FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_whatsapp_message():
    """Sample WhatsApp message for testing."""
    return {
        "phone": "5511999999999",
        "message": "Olá, gostaria de agendar uma consulta",
        "timestamp": "2024-01-15T10:30:00Z",
        "user_name": "João Silva",
        "message_id": "msg_123456789"
    }


@pytest.fixture
def sample_medical_query():
    """Sample medical query for testing."""
    return {
        "phone": "5511999999999", 
        "message": "Quais são os horários de funcionamento da clínica?",
        "timestamp": "2024-01-15T10:30:00Z",
        "user_name": "Maria Santos",
        "message_id": "msg_987654321"
    }