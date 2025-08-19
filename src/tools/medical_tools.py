"""
Medical tools for CrewAI agents.
"""

from typing import Any, Dict, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from src.core.logging import get_logger

logger = get_logger(__name__)


class KnowledgeBaseInput(BaseModel):
    """Input for knowledge base search."""
    query: str = Field(..., description="Search query for the knowledge base")


class KnowledgeBaseTool(BaseTool):
    """Tool for searching medical knowledge base."""
    
    name: str = "knowledge_base_search"
    description: str = """
    Ferramenta para buscar informações na base de conhecimento médico da clínica.
    Use para encontrar informações sobre:
    - Procedimentos médicos
    - Orientações para pacientes
    - Protocolos da clínica
    - Informações sobre especialidades
    - Cuidados pré e pós procedimentos
    """
    args_schema = KnowledgeBaseInput
    
    def _run(self, query: str) -> str:
        """Search the knowledge base."""
        logger.info("Knowledge base search", query=query)
        
        # TODO: Implement actual knowledge base search
        # This would connect to Supabase and search through documents
        # For now, return placeholder information
        
        # Placeholder responses based on common queries
        knowledge_responses = {
            "horário": "Nossa clínica funciona de segunda a sexta das 8h às 18h, e sábados das 8h às 12h.",
            "endereço": "Estamos localizados na Rua das Flores, 123, Centro da cidade.",
            "especialidades": "Oferecemos: Clínica Geral, Cardiologia, Dermatologia, Ginecologia, Pediatria e Ortopedia.",
            "exames": "Realizamos diversos exames laboratoriais e de imagem. Para agendamento, entre em contato.",
            "convenios": "Trabalhamos com os principais convênios médicos. Consulte disponibilidade para seu plano.",
            "preparo": "O preparo para exames varia conforme o tipo. Sempre orientamos previamente sobre jejum e medicações.",
        }
        
        query_lower = query.lower()
        
        for key, response in knowledge_responses.items():
            if key in query_lower:
                logger.info("Knowledge base match found", key=key)
                return response
        
        # Default response for unknown queries
        return """
        Para informações específicas sobre este assunto, recomendo que entre em 
        contato diretamente com nossa recepção ou agende uma consulta com um 
        de nossos especialistas.
        """
    
    async def _arun(self, query: str) -> str:
        """Async version of the search."""
        return self._run(query)


class AppointmentInput(BaseModel):
    """Input for appointment operations."""
    operation: str = Field(..., description="Operation type: 'check_availability', 'schedule', 'reschedule', 'cancel'")
    details: str = Field(..., description="Additional details for the operation")


class AppointmentTool(BaseTool):
    """Tool for appointment-related operations."""
    
    name: str = "appointment_manager"
    description: str = """
    Ferramenta para operações relacionadas a agendamentos:
    - Verificar disponibilidade de horários
    - Informações sobre agendamento
    - Orientações sobre reagendamento
    - Políticas de cancelamento
    
    NÃO realiza agendamentos diretos - apenas fornece informações.
    Para agendamentos reais, a consulta deve ser escalada.
    """
    args_schema = AppointmentInput
    
    def _run(self, operation: str, details: str) -> str:
        """Handle appointment operations."""
        logger.info("Appointment operation", operation=operation, details=details)
        
        if operation == "check_availability":
            return """
            Para verificar disponibilidade de horários, posso ajudá-lo com informações gerais:
            
            - Segunda a sexta: 8h às 18h
            - Sábados: 8h às 12h
            - Consultas são agendadas a cada 30 minutos
            
            Para verificar disponibilidade específica e realizar o agendamento, 
            vou transferir você para nossa equipe de agendamentos.
            """
            
        elif operation == "schedule":
            return """
            Para realizar um novo agendamento, preciso transferir você para nossa 
            equipe especializada que tem acesso direto à agenda médica.
            
            Eles poderão:
            - Verificar disponibilidade em tempo real
            - Confirmar seu convênio
            - Agendar no melhor horário para você
            
            Transferindo agora...
            """
            
        elif operation == "reschedule":
            return """
            Para reagendar sua consulta, nossa equipe de agendamentos poderá ajudar 
            verificando sua consulta atual e encontrando um novo horário.
            
            Transferindo para a equipe de reagendamentos...
            """
            
        elif operation == "cancel":
            return """
            Para cancelar sua consulta, lembre-se de nossa política:
            - Cancelamentos até 24h antes: sem cobrança
            - Cancelamentos com menos de 24h: sujeito a cobrança
            
            Nossa equipe de agendamentos fará o cancelamento para você.
            Transferindo...
            """
        
        return "Operação não reconhecida. Por favor, especifique o que precisa."
    
    async def _arun(self, operation: str, details: str) -> str:
        """Async version of appointment operations."""
        return self._run(operation, details)