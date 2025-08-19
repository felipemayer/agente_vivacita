"""
Tests for medical tools used by CrewAI agents.
"""

import pytest
from src.tools.medical_tools import KnowledgeBaseTool, AppointmentTool


class TestKnowledgeBaseTool:
    """Test cases for KnowledgeBaseTool."""
    
    def setup_method(self):
        """Setup for each test."""
        self.tool = KnowledgeBaseTool()
    
    def test_tool_properties(self):
        """Test tool basic properties."""
        assert self.tool.name == "knowledge_base_search"
        assert "base de conhecimento médico" in self.tool.description
        assert self.tool.args_schema is not None
    
    def test_search_clinic_hours(self):
        """Test searching for clinic hours."""
        queries = ["horário", "horários", "funcionamento", "que horas abre"]
        
        for query in queries:
            result = self.tool._run(query)
            assert "8h às 18h" in result
            assert "segunda a sexta" in result
    
    def test_search_clinic_address(self):
        """Test searching for clinic address."""
        queries = ["endereço", "localização", "onde fica", "address"]
        
        for query in queries:
            result = self.tool._run(query)
            assert "Rua das Flores" in result
    
    def test_search_specialties(self):
        """Test searching for medical specialties."""
        queries = ["especialidades", "médicos", "especialistas", "que especialidades"]
        
        for query in queries:
            result = self.tool._run(query)
            assert "Cardiologia" in result
            assert "Pediatria" in result
    
    def test_search_exams(self):
        """Test searching for exam information."""
        queries = ["exames", "laboratoriais", "exame de sangue"]
        
        for query in queries:
            result = self.tool._run(query)
            assert "exames laboratoriais" in result
            assert "agendamento" in result
    
    def test_search_insurance(self):
        """Test searching for insurance information."""
        queries = ["convênio", "plano de saúde", "convenios"]
        
        for query in queries:
            result = self.tool._run(query)
            assert "convênios médicos" in result
    
    def test_search_unknown_query(self):
        """Test searching for unknown information."""
        result = self.tool._run("informação inexistente sobre algo específico")
        assert "informações específicas" in result
        assert "entre em contato" in result
    
    def test_case_insensitive_search(self):
        """Test that search is case insensitive."""
        queries = ["HORÁRIO", "horário", "Horário", "HoRáRiO"]
        
        for query in queries:
            result = self.tool._run(query)
            assert "8h às 18h" in result
    
    @pytest.mark.asyncio
    async def test_async_search(self):
        """Test async version of search."""
        result = await self.tool._arun("horário")
        assert "8h às 18h" in result


class TestAppointmentTool:
    """Test cases for AppointmentTool."""
    
    def setup_method(self):
        """Setup for each test."""
        self.tool = AppointmentTool()
    
    def test_tool_properties(self):
        """Test tool basic properties."""
        assert self.tool.name == "appointment_manager"
        assert "agendamentos" in self.tool.description
        assert "NÃO realiza agendamentos diretos" in self.tool.description
    
    def test_check_availability(self):
        """Test checking appointment availability."""
        result = self.tool._run("check_availability", "consulta cardiologia")
        
        assert "8h às 18h" in result
        assert "a cada 30 minutos" in result
        assert "transferir você" in result
    
    def test_schedule_appointment(self):
        """Test appointment scheduling request."""
        result = self.tool._run("schedule", "consulta cardiologia segunda-feira")
        
        assert "transferir você" in result
        assert "equipe especializada" in result
        assert "agenda médica" in result
    
    def test_reschedule_appointment(self):
        """Test appointment rescheduling."""
        result = self.tool._run("reschedule", "mudar consulta de terça para quinta")
        
        assert "reagendar" in result
        assert "equipe de agendamentos" in result
        assert "Transferindo" in result
    
    def test_cancel_appointment(self):
        """Test appointment cancellation."""
        result = self.tool._run("cancel", "cancelar consulta de amanhã")
        
        assert "24h antes" in result
        assert "política" in result
        assert "Transferindo" in result
    
    def test_unknown_operation(self):
        """Test unknown operation handling."""
        result = self.tool._run("unknown_operation", "alguma coisa")
        
        assert "Operação não reconhecida" in result
        assert "especifique" in result
    
    @pytest.mark.asyncio
    async def test_async_operations(self):
        """Test async version of operations."""
        result = await self.tool._arun("check_availability", "teste")
        assert "transferir você" in result