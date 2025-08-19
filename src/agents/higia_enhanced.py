#!/usr/bin/env python3
"""
Hígia Enhanced - Assistente Virtual da Clínica Vivacità com Integração MCP
Versão aprimorada com VivacitaMCPTool para agendamentos médicos inteligentes
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

from src.core.config import settings
from src.core.logging import get_logger
from src.tools.vivacita_mcp_tool import VivacitaMCPTool, create_vivacita_tool
from src.knowledge.vivacita_clinic_kb import vivacita_kb

logger = get_logger(__name__)

class HigiaEnhancedAgent:
    """
    Hígia Enhanced - Assistente Virtual da Clínica Vivacità com MCP Integration
    
    Nova versão com:
    - Integração VivacitaMCPTool para agendamentos reais
    - Base de conhecimento atualizada com especialidades reais
    - Validação inteligente de regras da clínica
    - Suporte completo às capacidades especiais do Dr. Ernesto
    """
    
    def __init__(self):
        """Initialize enhanced Hígia agent with MCP integration."""
        
        # Initialize LLM (using OpenAI for now, can switch to OpenRouter later)
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=4000
        )
        
        # Initialize MCP tool
        self.vivacita_tool = create_vivacita_tool()
        
        # Initialize knowledge base
        self.kb = vivacita_kb
        
        # Create enhanced Hígia agent
        self.higia = Agent(
            role='Assistente Virtual Hígia - Especialista em Saúde Mental da Clínica Vivacità',
            goal='''Sou Hígia, assistente virtual da Clínica Vivacità Saúde Mental.
            Minha missão é proporcionar atendimento humanizado, empático e eficiente,
            priorizando o bem-estar dos pacientes e facilitando agendamentos médicos.''',
            
            backstory=f'''Sou Hígia, nomeada em honra à deusa grega da saúde.
            Trabalho na Clínica Vivacità Saúde Mental como assistente virtual especializada.
            
            PERSONALIDADE:
            - Educada, respeitosa e empática
            - Tom feminino, suave e acolhedor
            - Formal mas próxima, uso "você" (nunca "tu")
            - Linguagem natural e conversacional
            - Tranquilizadora em situações de ansiedade
            
            CONHECIMENTO ATUALIZADO DA CLÍNICA:
            {self.kb.get_clinic_summary()}
            
            REGRAS FUNDAMENTAIS:
            1. SEMPRE usar a ferramenta vivacita_scheduler para consultas médicas
            2. Dr. Ernesto é ÚNICO para: crianças 7+, consultas online, relatórios
            3. Horários online fixos: 11:45, 17:00, 17:15 (apenas Dr. Ernesto)
            4. Validar idade antes de agendar (mínimo 7 anos)
            5. Para emergências: encaminhar para atendimento especializado
            6. Coletar dados completos antes de finalizar agendamentos
            
            FLUXO DE AGENDAMENTO INTELIGENTE:
            1. Identificar necessidade e validar elegibilidade
            2. Determinar médico adequado pelas regras da clínica
            3. Verificar disponibilidade real usando a ferramenta
            4. Coletar dados do paciente
            5. Validar agendamento antes de confirmar
            6. Orientar paciente sobre preparação e comparecimento
            ''',
            
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self.vivacita_tool]
        )
    
    async def process_message(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming message with enhanced MCP integration.
        
        Args:
            context: Message context with routing information
            
        Returns:
            Processing result with response and metadata
        """
        message = context.get("message", "")
        phone = context.get("phone", "")
        name = context.get("name", "")
        routing_result = context.get("routing_result", {})
        
        logger.info(
            "Hígia Enhanced processing message",
            phone=phone,
            workflow=routing_result.get("workflow", "general"),
            priority=routing_result.get("priority", "normal")
        )
        
        try:
            # Create intelligent task description
            task_description = self._create_enhanced_task_description(
                message, routing_result, name, phone
            )
            
            # Create the task for Hígia
            task = Task(
                description=task_description,
                expected_output="Resposta empática, profissional e completa seguindo as diretrizes da Hígia Enhanced",
                agent=self.higia
            )
            
            # Create crew with enhanced agent
            crew = Crew(
                agents=[self.higia],
                tasks=[task],
                verbose=False  # Reduced verbosity for cleaner logs
            )
            
            # Execute with performance tracking
            start_time = datetime.utcnow()
            result = crew.kickoff()
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Enhanced escalation logic
            escalate = self._enhanced_escalation_check(message, routing_result, str(result))
            
            return {
                "status": "success",
                "response": str(result),
                "escalate": escalate,
                "processing_time": processing_time,
                "agent_used": "higia_enhanced",
                "workflow": routing_result.get("workflow", "general"),
                "priority": routing_result.get("priority", "normal"),
                "mcp_integration": True,
                "knowledge_base": "vivacita_real_specialties"
            }
            
        except Exception as e:
            logger.error(
                "Error in Hígia Enhanced processing",
                phone=phone,
                error=str(e),
                exc_info=True
            )
            
            return {
                "status": "error",
                "response": self._get_enhanced_fallback_response(name),
                "escalate": True,
                "error": str(e),
                "agent_used": "higia_enhanced"
            }
    
    def _create_enhanced_task_description(
        self, 
        message: str, 
        routing_result: Dict[str, Any], 
        name: str = "", 
        phone: str = ""
    ) -> str:
        """Create enhanced task description with MCP integration context."""
        
        workflow = routing_result.get("workflow", "general")
        priority = routing_result.get("priority", "normal")
        current_time = datetime.now()
        
        # Base context with enhanced information
        base_context = f"""
        CONTEXTO HÍGIA ENHANCED:
        Data/Hora atual: {current_time.strftime('%d/%m/%Y %H:%M')}
        Paciente: {name or 'Não informado'}
        Telefone: {phone or 'Não informado'}
        Workflow detectado: {workflow}
        Prioridade: {priority}
        
        MENSAGEM DO PACIENTE: "{message}"
        
        FERRAMENTA DISPONÍVEL:
        - vivacita_scheduler: Sistema completo de agendamento médico
        
        IMPORTANTE: Use SEMPRE a ferramenta vivacita_scheduler para:
        - Consultar especialidades: vivacita_scheduler(action="get_specialties")
        - Informações Dr. Ernesto: vivacita_scheduler(action="get_dr_ernesto")
        - Verificar disponibilidade: vivacita_scheduler(action="check_availability")
        - Validar agendamento: vivacita_scheduler(action="validate_appointment")
        - Consultar preços: vivacita_scheduler(action="get_prices")
        - Verificar elegibilidade criança: vivacita_scheduler(action="check_child_eligibility", age=X)
        - Opções online: vivacita_scheduler(action="get_online_options")
        """
        
        # Emergency handling
        if priority == "high" or workflow == "emergency_escalation":
            return base_context + """
            🚨 SITUAÇÃO DE EMERGÊNCIA DETECTADA!
            
            AÇÃO IMEDIATA:
            1. Responda com máxima empatia e urgência
            2. Reconheça a situação com seriedade
            3. Oriente para buscar ajuda médica imediata
            4. Forneça contatos de emergência:
               - SAMU: 192
               - CVV: 188 (24h)
               - Emergência psiquiátrica mais próxima
            5. Tranquilize mas seja firme na orientação
            6. Escale IMEDIATAMENTE para equipe médica
            
            LINGUAGEM: Empática, tranquilizadora, mas com urgência apropriada.
            NÃO minimize a situação, ofereça suporte real e imediato.
            """
        
        # Appointment booking workflow
        elif workflow in ["appointment_booking", "appointment_confirmation", "appointment_rescheduling"]:
            return base_context + """
            📅 AGENDAMENTO MÉDICO INTELIGENTE
            
            FLUXO OBRIGATÓRIO - Use as ferramentas nesta ordem:
            
            1. PRIMEIRO: Identifique a necessidade
               - Especialidade desejada
               - Idade do paciente (crítico para validação)
               - Preferência de modalidade (presencial/online)
               - Tipo especial (relatório, consulta criança)
            
            2. VALIDAÇÃO: vivacita_scheduler(action="validate_appointment", patient_age=X, specialty="Y", modality="Z")
            
            3. INFORMAÇÕES: 
               - Para Dr. Ernesto: vivacita_scheduler(action="get_dr_ernesto")
               - Para preços: vivacita_scheduler(action="get_prices")
               - Para criança: vivacita_scheduler(action="check_child_eligibility", age=X)
               - Para online: vivacita_scheduler(action="get_online_options")
            
            4. DISPONIBILIDADE: vivacita_scheduler(action="check_availability", doctor_id=X, date="YYYY-MM-DD")
            
            5. COLETA DE DADOS (se tudo OK):
               "Para prosseguir com seu agendamento, preciso dos seguintes dados:
               ➡️ Nome completo
               ➡️ Data de nascimento
               ➡️ CPF
               ➡️ Telefone
               ➡️ Email
               ➡️ Endereço completo com CEP
               ➡️ Convênio (se houver)
               ➡️ Foto do documento e carteirinha (se convênio)"
            
            REGRAS CRÍTICAS:
            - Crianças 7-17 anos: APENAS Dr. Ernesto
            - Consultas online: APENAS Dr. Ernesto (11:45, 17:00, 17:15)
            - Relatórios médicos: APENAS Dr. Ernesto
            - Idade mínima: 7 anos
            - Horário mínimo hoje: +2 horas da hora atual
            
            LINGUAGEM: Profissional, clara, acolhedora. Explique as regras especiais quando aplicáveis.
            """
        
        # General medical consultation
        else:
            return base_context + """
            💬 CONSULTA MÉDICA GERAL E INFORMAÇÕES
            
            ABORDAGEM INTELIGENTE:
            
            1. Para perguntas sobre especialidades:
               vivacita_scheduler(action="get_specialties")
            
            2. Para informações sobre a clínica:
               vivacita_scheduler(action="get_clinic_info")
            
            3. Para questões de preços:
               vivacita_scheduler(action="get_prices")
            
            4. Para perguntas sobre Dr. Ernesto:
               vivacita_scheduler(action="get_dr_ernesto")
            
            5. Para consultas online:
               vivacita_scheduler(action="get_online_options")
            
            ORIENTAÇÕES GERAIS:
            - Seja empática e acolhedora
            - Forneça informações precisas usando as ferramentas
            - Explique claramente as opções disponíveis
            - Oriente sobre próximos passos quando apropriado
            - Para situações complexas, ofereça transferir para atendente humano
            
            ESPECIALIDADES DISPONÍVEIS:
            - Psiquiatria (R$ 500,00)
            - Psicologia (R$ 250,00 particular / R$ 150,00 Bradesco)
            - Neuropsicologia (R$ 1.950,00)
            - Exames diversos
            - Polissonografia (exame do sono)
            
            HORÁRIO DA CLÍNICA: Segunda a Sexta, 08:00-18:00
            
            LINGUAGEM: Natural, informativa, tranquilizadora, sempre profissional.
            """
    
    def _enhanced_escalation_check(
        self, 
        message: str, 
        routing_result: Dict[str, Any], 
        response: str
    ) -> bool:
        """Enhanced escalation logic with multiple criteria."""
        
        # Emergency situations always escalate
        if routing_result.get("priority") == "high":
            logger.warning("Escalating due to high priority routing")
            return True
        
        # Enhanced emergency keywords
        emergency_keywords = [
            "suicídio", "suicidio", "desespero", "autolesão", "autolesao",
            "não aguento mais", "nao aguento mais", "acabar com tudo",
            "me matar", "morrer", "não vale a pena", "nao vale a pena",
            "sem saída", "sem saida", "não tem jeito", "nao tem jeito",
            "vou me matar", "quero morrer", "penso em morrer"
        ]
        
        message_lower = message.lower()
        for keyword in emergency_keywords:
            if keyword in message_lower:
                logger.warning(f"Escalating due to emergency keyword: {keyword}")
                return True
        
        # Complex situation indicators
        complex_indicators = [
            "não entendi", "nao entendi", "confuso", "não ficou claro",
            "preciso falar com alguém", "quero falar com atendente",
            "isso não resolve", "isso nao resolve", "muito complicado"
        ]
        
        for indicator in complex_indicators:
            if indicator in message_lower:
                logger.info(f"Escalating due to complexity indicator: {indicator}")
                return True
        
        # Check if response contains error indicators
        error_indicators = ["erro", "problema", "não foi possível", "nao foi possivel"]
        response_lower = response.lower()
        for indicator in error_indicators:
            if indicator in response_lower:
                logger.info(f"Escalating due to response error indicator: {indicator}")
                return True
        
        return False
    
    def _get_enhanced_fallback_response(self, name: str = "") -> str:
        """Enhanced fallback response with personalization."""
        greeting = f"Olá {name}! " if name else "Olá! "
        
        return f"""{greeting}Peço desculpas, mas estou enfrentando algumas dificuldades técnicas no momento.
        
        Para garantir que você receba o melhor atendimento possível, vou transferir você para um de nossos atendentes especializados que poderá ajudá-lo imediatamente.
        
        Não se preocupe, estamos aqui para cuidar do seu bem-estar e resolver sua necessidade da melhor forma possível.
        
        Aguarde um momento, por favor. 💙
        
        --- Hígia Enhanced ---
        Clínica Vivacità Saúde Mental"""

    def test_mcp_integration(self) -> Dict[str, Any]:
        """Test MCP tool integration for validation."""
        
        test_results = {
            "tool_loaded": False,
            "specialties_test": False,
            "dr_ernesto_test": False,
            "validation_test": False,
            "errors": []
        }
        
        try:
            # Test 1: Tool loading
            if self.vivacita_tool:
                test_results["tool_loaded"] = True
                logger.info("✅ VivacitaMCPTool loaded successfully")
            
            # Test 2: Get specialties
            specialties_result = self.vivacita_tool._run("get_specialties")
            if "PSIQUIATRA" in specialties_result:
                test_results["specialties_test"] = True
                logger.info("✅ Specialties retrieval working")
            
            # Test 3: Dr. Ernesto info
            ernesto_result = self.vivacita_tool._run("get_dr_ernesto")
            if "ERNESTO" in ernesto_result:
                test_results["dr_ernesto_test"] = True
                logger.info("✅ Dr. Ernesto info retrieval working")
            
            # Test 4: Validation
            validation_result = self.vivacita_tool._run(
                "validate_appointment", 
                patient_age=10, 
                specialty="PSIQUIATRA", 
                modality="presencial"
            )
            if "valid" in validation_result:
                test_results["validation_test"] = True
                logger.info("✅ Appointment validation working")
                
        except Exception as e:
            error_msg = f"MCP integration test error: {str(e)}"
            test_results["errors"].append(error_msg)
            logger.error(error_msg)
        
        return test_results

# Factory function for easy instantiation
def create_higia_enhanced() -> HigiaEnhancedAgent:
    """Create and return enhanced Hígia agent instance."""
    return HigiaEnhancedAgent()

# Test integration when run directly
if __name__ == "__main__":
    print("🚀 Testing Hígia Enhanced with MCP Integration...")
    
    higia = create_higia_enhanced()
    test_results = higia.test_mcp_integration()
    
    print(f"Test Results: {test_results}")
    
    if all([test_results["tool_loaded"], test_results["specialties_test"], 
            test_results["dr_ernesto_test"], test_results["validation_test"]]):
        print("✅ All MCP integration tests passed!")
    else:
        print("⚠️ Some MCP integration tests failed.")
        if test_results["errors"]:
            print(f"Errors: {test_results['errors']}")