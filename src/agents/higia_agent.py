"""
Hígia - Assistente Virtual da Clínica Vivacità Saúde Mental
Seguindo exatamente o prompt original definido em .docs/original_prompt.md
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from crewai import Agent, Task, Crew
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from src.core.config import settings
from src.core.logging import get_logger
from src.tools.higia_tools import (
    RAGKnowledgeTool,
    ListaMedicosTool,
    DisponibilidadeTool,
    CriarConsultaTool,
    TeleconsultaErnestoTool
)

logger = get_logger(__name__)


class HigiaAgent:
    """
    Hígia - Assistente Virtual da Clínica Vivacità Saúde Mental
    
    Identidade: Assistente empática, educada e profissional especializada em saúde mental
    Personalidade: Feminina, suave, acolhedora, formal mas próxima
    Missão: Atendimento humano via WhatsApp priorizando bem-estar dos pacientes
    """
    
    def __init__(self):
        """Initialize Hígia agent with original prompt specifications."""
        # Initialize OpenRouter LLM for Claude Sonnet 4
        self.llm = ChatOpenAI(
            model=settings.OPENROUTER_MODEL,
            openai_api_key=settings.OPENROUTER_API_KEY,
            openai_api_base=settings.OPENROUTER_BASE_URL,
            temperature=0.7,
            max_tokens=4000
        )
        
        # Initialize Hígia's specific tools
        self.rag_tool = RAGKnowledgeTool()
        self.lista_medicos_tool = ListaMedicosTool()
        self.disponibilidade_tool = DisponibilidadeTool()
        self.criar_consulta_tool = CriarConsultaTool()
        self.teleconsulta_ernesto_tool = TeleconsultaErnestoTool()
        
        # Create the unified Hígia agent
        self.higia = Agent(
            role='Assistente Virtual Especializada em Saúde Mental',
            goal='''Sou Hígia, assistente virtual da Clínica Vivacità Saúde Mental.
            Minha missão é proporcionar atendimento humano, empático e eficiente,
            priorizando sempre o bem-estar dos pacientes via WhatsApp.''',
            
            backstory='''Sou Hígia, nomeada em honra à deusa grega da saúde.
            Trabalho na Clínica Vivacità Saúde Mental como assistente virtual especializada.
            
            PERSONALIDADE:
            - Educada e respeitosa
            - Cordial e calorosa  
            - Empática e compreensiva
            - Tranquilizadora
            - Tom feminino, suave e acolhedor
            - Formal mas próxima
            - Uso "você" (nunca "tu")
            - Linguagem natural e conversacional
            
            REGRAS FUNDAMENTAIS:
            1. SEMPRE consultar lista_medicos para obter doctor_id correto
            2. CONFIRMAR nome do médico com paciente antes de consultar disponibilidade
            3. Usar APENAS horários de available_slots da API
            4. NUNCA calcular horários manualmente
            5. Horário mínimo para hoje: 2h de antecedência
            6. Para emergências: palavras-chave suicídio, desespero, autolesão, "não aguento mais"
            7. NÃO existe "retorno gratuito" - NUNCA usar palavra "retorno"
            
            FLUXO DE AGENDAMENTO:
            1. Identificar necessidade (Psiquiatria/Psicologia/Avaliação)
            2. Coletar dados com mensagem padrão
            3. Consultar disponibilidade com doctor_id
            4. Oferecer apenas available_slots válidos
            5. Criar agendamento e orientar paciente
            ''',
            
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[
                self.rag_tool,
                self.lista_medicos_tool,
                self.disponibilidade_tool,
                self.criar_consulta_tool,
                self.teleconsulta_ernesto_tool
            ]
        )
    
    async def process_message(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming message following Hígia's original specifications.
        
        Args:
            context: Message context with routing information
            
        Returns:
            Processing result with response and metadata
        """
        message = context.get("message", "")
        phone = context.get("phone", "")
        routing_result = context.get("routing_result", {})
        
        logger.info(
            "Hígia processing message",
            phone=phone,
            workflow=routing_result.get("workflow", "general"),
            priority=routing_result.get("priority", "normal")
        )
        
        try:
            # Determine the specific task based on routing
            task_description = self._create_task_description(message, routing_result)
            
            # Create the task for Hígia
            task = Task(
                description=task_description,
                expected_output="Resposta empática e profissional seguindo as diretrizes da Hígia",
                agent=self.higia
            )
            
            # Create crew with single agent
            crew = Crew(
                agents=[self.higia],
                tasks=[task],
                verbose=True
            )
            
            # Execute the task
            start_time = datetime.utcnow()
            result = crew.kickoff()
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Determine if escalation is needed
            escalate = self._should_escalate(message, routing_result)
            
            return {
                "status": "success",
                "response": str(result),
                "escalate": escalate,
                "processing_time": processing_time,
                "agent_used": "higia",
                "workflow": routing_result.get("workflow", "general"),
                "priority": routing_result.get("priority", "normal")
            }
            
        except Exception as e:
            logger.error(
                "Error in Hígia processing",
                phone=phone,
                error=str(e),
                exc_info=True
            )
            
            # Return empathetic error response
            return {
                "status": "error",
                "response": self._get_fallback_response(),
                "escalate": True,
                "error": str(e)
            }
    
    def _create_task_description(self, message: str, routing_result: Dict[str, Any]) -> str:
        """Create specific task description based on routing result."""
        workflow = routing_result.get("workflow", "general")
        priority = routing_result.get("priority", "normal")
        
        # Base context for all interactions
        base_context = f"""
        CONTEXTO ATUAL:
        Data atual: {datetime.now().strftime('%d/%m/%Y')}
        Hora atual: {datetime.now().strftime('%H:%M')}
        Horário mínimo para hoje: {(datetime.now() + timedelta(hours=2)).strftime('%H:%M')}
        
        MENSAGEM DO PACIENTE: "{message}"
        
        INSTRUÇÕES ESPECÍFICAS:
        """
        
        if priority == "high" or workflow == "emergency_escalation":
            return base_context + """
            SITUAÇÃO DE EMERGÊNCIA DETECTADA!
            
            1. Responda com empatia e urgência
            2. Consulte "Hígia - RAG - Diretrizes de Atendimento" 
            3. Transfira IMEDIATAMENTE para equipe médica
            4. Use linguagem tranquilizadora mas tome ação rápida
            5. Palavras-chave detectadas indicam risco - priorize segurança
            
            Seja Hígia: empática, profissional, mas aja com urgência médica.
            """
            
        elif workflow in ["appointment_booking", "appointment_confirmation", "appointment_rescheduling"]:
            return base_context + """
            AGENDAMENTO MÉDICO - Siga o fluxo obrigatório:
            
            1. PRIMEIRO: Use lista_medicos para obter doctor_id correto
            2. Confirme nome do médico com o paciente
            3. Use disponibilidade_agenda_medico com doctor_id
            4. Ofereça APENAS horários de available_slots
            5. Filtre horários válidos para hoje (>= agora + 2h)
            6. Se necessário, colete dados com mensagem padrão:
               "Para seguirmos com seu agendamento nos informe, por gentileza, os dados solicitados abaixo:
               ➡️Nome completo
               ➡️Data de nascimento  
               ➡️Convênio
               ➡️CPF
               ➡️Endereço com Cep
               ➡️ENCAMINCAR DOCUMENTO PESSOAL + CARTEIRINHA DO CONVÊNIO"
            
            LEMBRE-SE:
            - Dr. Ernesto: Único para crianças (7+ anos), laudos e teleconsulta
            - NÃO existe "retorno gratuito" - NUNCA use "retorno"
            - Consulte "Hígia - RAG - Lista de Convênios" se necessário
            
            Seja Hígia: acolhedora, profissional, siga protocolos rigorosamente.
            """
            
        else:  # General medical consultation
            return base_context + """
            CONSULTA MÉDICA GERAL - Informações e orientações:
            
            1. Consulte "Hígia - RAG - Sobre a Vivacità" para informações da clínica
            2. Se perguntarem sobre convênios: use "Hígia - RAG - Lista de Convênios"
            3. Para diretrizes específicas: use "Hígia - RAG - Diretrizes de Atendimento"
            4. Se perguntarem sobre valores, use tabela específica:
               - Consulta Psiquiátrica: R$ 500,00
               - Psicoterapia: R$ 250,00 (R$ 150,00 Bradesco)
               - Laudos: R$ 500,00
            5. Para avaliações, use mensagem padrão dos valores
            6. Dúvidas sobre exames → Ana Clara
            7. Situações complexas → atendente humano
            
            Seja Hígia: empática, informativa, tranquilizadora, sempre profissional.
            """
    
    def _should_escalate(self, message: str, routing_result: Dict[str, Any]) -> bool:
        """Determine if message should be escalated to human staff."""
        # Emergency situations always escalate
        if routing_result.get("priority") == "high":
            return True
            
        # Emergency keywords
        emergency_keywords = [
            "suicídio", "suicidio", "desespero", "autolesão", "autolesao", 
            "não aguento mais", "nao aguento mais", "acabar com tudo",
            "me matar", "morrer", "não vale a pena", "nao vale a pena"
        ]
        
        message_lower = message.lower()
        for keyword in emergency_keywords:
            if keyword in message_lower:
                return True
                
        return False
    
    def _get_fallback_response(self) -> str:
        """Get empathetic fallback response for errors."""
        return """Peço desculpas, mas estou enfrentando algumas dificuldades técnicas no momento. 
        
        Para garantir que você receba o melhor atendimento, vou transferir você para um de nossos atendentes que poderá ajudá-lo imediatamente.
        
        Aguarde um momento, por favor. Estou aqui para cuidar do seu bem-estar. 💙"""


# Legacy compatibility - maintain the same interface
class MedicalCrew:
    """Legacy compatibility class that now uses Hígia agent."""
    
    def __init__(self):
        """Initialize with Hígia agent."""
        self.higia_agent = HigiaAgent()
    
    async def process_consultation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process consultation using Hígia agent."""
        return await self.higia_agent.process_message(context)