"""
Ferramentas específicas para a Hígia seguindo o prompt original.
Implementa APIs médicas e sistema RAG conforme especificado.
"""

from typing import Any, Dict, List, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import json

from src.core.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# SISTEMA RAG - Base de Conhecimento
# =============================================================================

class RAGQueryInput(BaseModel):
    """Input for RAG knowledge base queries."""
    query: str = Field(..., description="Consulta para a base de conhecimento")
    source: str = Field(..., description="Fonte específica: 'diretrizes', 'convenios', ou 'sobre_vivacita'")


class RAGKnowledgeTool(BaseTool):
    """Sistema RAG conforme especificado no prompt original."""
    
    name: str = "rag_knowledge_base"
    description: str = """
    Sistema de conhecimento RAG da Hígia com 3 fontes:
    1. "diretrizes" - Hígia RAG Diretrizes de Atendimento (protocolos e emergências)
    2. "convenios" - Hígia RAG Lista de Convênios (convênios aceitos)
    3. "sobre_vivacita" - Hígia RAG Sobre a Vivacità (informações da clínica)
    """
    args_schema = RAGQueryInput
    
    def _run(self, query: str, source: str) -> str:
        """Query the RAG knowledge base."""
        logger.info("RAG query", query=query, source=source)
        
        # Conhecimento base da Vivacità Saúde Mental
        knowledge_base = {
            "diretrizes": {
                "emergencia_suicidio": """
                PROTOCOLO DE EMERGÊNCIA - RISCO SUICIDA:
                1. NUNCA minimizar ou descartar sinais
                2. Ouvir com empatia sem julgar
                3. Transferir IMEDIATAMENTE para plantão médico
                4. Manter contato até chegada da equipe
                5. Telefone emergência: (11) 99999-9999
                6. Em casos extremos: orientar procurar PS ou SAMU 192
                """,
                "protocolo_agendamento": """
                PROTOCOLO DE AGENDAMENTO:
                1. Identificar necessidade (Psiquiatria/Psicologia/Avaliação)
                2. Confirmar médico e obter doctor_id
                3. Consultar API disponibilidade_agenda_medico
                4. Usar APENAS available_slots
                5. Filtrar horários válidos (hoje >= +2h)
                6. Coletar dados completos do paciente
                7. Criar agendamento e orientar
                """,
                "orientacoes_consulta": """
                ORIENTAÇÕES PARA CONSULTA:
                - Chegar 15 minutos antes do horário
                - Documentos obrigatórios: RG/CPF + carteirinha convênio
                - Não faltar sem aviso prévio
                - Consultas pagas: PIX, cartão ou dinheiro
                - Reserva temporária - clínica confirmará por telefone
                """
            },
            
            "convenios": {
                "aceitos": """
                CONVÊNIOS ACEITOS NA VIVACITÀ:
                
                ✅ BRADESCO SAÚDE
                - Psicoterapia: R$ 150,00 (com cobertura)
                - Consulta psiquiátrica: verificar cobertura
                
                ✅ AMIL
                - Verificar cobertura específica do plano
                
                ✅ UNIMED
                - Verificar cobertura específica do plano
                
                ✅ SULAMERICA
                - Verificar cobertura específica do plano
                
                ❌ PREVENT SENIOR
                - Não atendemos este convênio
                
                IMPORTANTE: Sempre verificar cobertura antes do agendamento.
                Para dúvidas específicas, falar com Ana Clara.
                """,
                "particular": """
                VALORES PARTICULARES:
                - Consulta Psiquiátrica: R$ 500,00
                - Psicoterapia: R$ 250,00
                - Laudos médicos: R$ 500,00
                - Formas de pagamento: PIX, cartão, dinheiro
                """
            },
            
            "sobre_vivacita": {
                "clinica": """
                CLÍNICA VIVACITÀ SAÚDE MENTAL
                
                🏥 ESPECIALIDADES:
                - Psiquiatria Geral
                - Psicologia/Psicoterapia
                - Psiquiatria Infantil (Dr. Ernesto - 7+ anos)
                - Avaliação Neuropsicológica
                - Avaliação Psicológica
                - Laudos médicos
                
                👨‍⚕️ PROFISSIONAIS:
                - Dr. Ernesto: Crianças 7+, laudos, teleconsulta
                - Equipe especializada em saúde mental
                
                📍 LOCALIZAÇÃO:
                - Endereço: [Consultar recepção]
                - Horários: Verificar agenda de cada profissional
                
                📞 CONTATO:
                - WhatsApp: Este número
                - Emergências: Transferência imediata
                """,
                "avaliacoes": """
                VALORES DAS AVALIAÇÕES:
                
                • AVALIAÇÃO NEUROPSICOLÓGICA:
                    • R$ 1.950,00 À VISTA (dinheiro, débito ou PIX)
                    • R$ 2.100,00 PARCELADO EM 4X
                
                • AVALIAÇÃO PSICOLÓGICA:
                    • R$ 1.350,00 À VISTA (dinheiro, débito ou PIX)  
                    • R$ 1.450,00 PARCELADO EM 4X
                
                Cada sessão será realizada uma vez na semana, com horários e dias fixos.
                Em média, a avaliação demanda de 5 a 10 sessões até sua conclusão final.
                """,
                "teleconsulta": """
                TELECONSULTAS:
                - Disponível apenas com Dr. Ernesto
                - Consulte horários específicos via API
                - Mesmos valores da consulta presencial
                - Plataforma será informada no agendamento
                """
            }
        }
        
        # Buscar informação relevante
        if source in knowledge_base:
            source_data = knowledge_base[source]
            
            # Busca por palavras-chave
            query_lower = query.lower()
            
            for key, content in source_data.items():
                if any(word in key.lower() for word in query_lower.split()):
                    return content
                    
            # Se não encontrou match específico, retorna informação geral
            if source == "diretrizes":
                return source_data.get("protocolo_agendamento", "Consulte as diretrizes específicas.")
            elif source == "convenios":
                return source_data.get("aceitos", "Consulte a lista de convênios aceitos.")
            else:
                return source_data.get("clinica", "Consulte informações sobre a Vivacità.")
        
        return f"Informação não encontrada na fonte {source}. Consulte atendente para detalhes."
    
    async def _arun(self, query: str, source: str) -> str:
        """Async version of RAG query."""
        return self._run(query, source)


# =============================================================================
# APIS MÉDICAS
# =============================================================================

class ListaMedicosInput(BaseModel):
    """Input for doctors list API."""
    specialty: str = Field(default="all", description="Especialidade: 'psiquiatria', 'psicologia', 'all'")


class ListaMedicosTool(BaseTool):
    """API para listar médicos com horários de funcionamento."""
    
    name: str = "lista_medicos"
    description: str = """
    Lista médicos disponíveis com seus horários específicos de funcionamento.
    Retorna doctor_id que deve ser usado nas outras APIs.
    SEMPRE consulte esta API primeiro para obter o doctor_id correto.
    """
    args_schema = ListaMedicosInput
    
    def _run(self, specialty: str = "all") -> str:
        """Get list of doctors."""
        logger.info("Consulting doctors list", specialty=specialty)
        
        # Base de dados dos médicos (simulada)
        doctors = [
            {
                "doctor_id": "dr_ernesto_001",
                "name": "Dr. Ernesto Silva",
                "specialty": "psiquiatria",
                "special_features": ["criancas_7_anos", "laudos_medicos", "teleconsulta"],
                "working_hours": "08:00-18:00",
                "working_days": ["segunda", "terca", "quarta", "quinta", "sexta"]
            },
            {
                "doctor_id": "dra_maria_002", 
                "name": "Dra. Maria Santos",
                "specialty": "psicologia",
                "special_features": ["psicoterapia", "avaliacao_psicologica"],
                "working_hours": "14:00-20:00",
                "working_days": ["segunda", "terca", "quarta", "quinta"]
            },
            {
                "doctor_id": "dr_carlos_003",
                "name": "Dr. Carlos Oliveira", 
                "specialty": "psiquiatria",
                "special_features": ["psiquiatria_geral"],
                "working_hours": "09:00-17:00",
                "working_days": ["terca", "quarta", "quinta", "sexta", "sabado"]
            }
        ]
        
        # Filtrar por especialidade se especificado
        if specialty != "all":
            doctors = [d for d in doctors if d["specialty"] == specialty]
        
        return json.dumps(doctors, indent=2, ensure_ascii=False)
    
    async def _arun(self, specialty: str = "all") -> str:
        """Async version of doctors list."""
        return self._run(specialty)


class DisponibilidadeInput(BaseModel):
    """Input for availability API."""
    doctor_id: str = Field(..., description="ID do médico obtido via lista_medicos")
    date: str = Field(..., description="Data no formato YYYY-MM-DD")


class DisponibilidadeTool(BaseTool):
    """API para consultar disponibilidade de agenda do médico."""
    
    name: str = "disponibilidade_agenda_medico"
    description: str = """
    Consulta horários ocupados de um médico específico.
    CRÍTICO: Use o doctor_id obtido via lista_medicos.
    Retorna available_slots (use APENAS estes) e busy_slots (apenas referência).
    """
    args_schema = DisponibilidadeInput
    
    def _run(self, doctor_id: str, date: str) -> str:
        """Check doctor availability."""
        logger.info("Checking availability", doctor_id=doctor_id, date=date)
        
        # Simular consulta de disponibilidade
        try:
            requested_date = datetime.strptime(date, "%Y-%m-%d")
            current_time = datetime.now()
            
            # Horários base por médico
            doctor_schedules = {
                "dr_ernesto_001": {
                    "working_hours": "08:00-18:00",
                    "slot_duration": 60,  # minutos
                    "base_slots": ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"]
                },
                "dra_maria_002": {
                    "working_hours": "14:00-20:00", 
                    "slot_duration": 60,
                    "base_slots": ["14:00", "15:00", "16:00", "17:00", "18:00", "19:00"]
                },
                "dr_carlos_003": {
                    "working_hours": "09:00-17:00",
                    "slot_duration": 60,
                    "base_slots": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]
                }
            }
            
            if doctor_id not in doctor_schedules:
                return json.dumps({
                    "error": "Doctor ID inválido",
                    "available_slots": [],
                    "doctor_working_hours": {"working_hours": "N/A", "busy_slots": []}
                })
            
            schedule = doctor_schedules[doctor_id]
            
            # Simular alguns horários ocupados
            import random
            all_slots = schedule["base_slots"]
            busy_count = random.randint(1, len(all_slots) // 2)
            busy_slots = random.sample(all_slots, busy_count)
            
            # Available slots = todos os slots - busy slots
            available_slots = []
            for slot in all_slots:
                if slot not in busy_slots:
                    # Se for hoje, verificar regra de 2h antecedência
                    if requested_date.date() == current_time.date():
                        slot_time = datetime.strptime(f"{date} {slot}:00", "%Y-%m-%d %H:%M:%S")
                        min_time = current_time + timedelta(hours=2)
                        if slot_time >= min_time:
                            available_slots.append({"start_time": f"{slot}:00", "status": "available"})
                    else:
                        available_slots.append({"start_time": f"{slot}:00", "status": "available"})
            
            result = {
                "available_slots": available_slots,
                "doctor_working_hours": {
                    "working_hours": schedule["working_hours"],
                    "busy_slots": [f"{slot}:00" for slot in busy_slots]
                },
                "date": date,
                "doctor_id": doctor_id
            }
            
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error("Error checking availability", error=str(e))
            return json.dumps({
                "error": f"Erro ao consultar disponibilidade: {str(e)}",
                "available_slots": [],
                "doctor_working_hours": {"working_hours": "N/A", "busy_slots": []}
            })
    
    async def _arun(self, doctor_id: str, date: str) -> str:
        """Async version of availability check."""
        return self._run(doctor_id, date)


class CriarConsultaInput(BaseModel):
    """Input for creating appointment."""
    patient_name: str = Field(..., description="Nome completo do paciente")
    patient_birth: str = Field(..., description="Data nascimento (DD/MM/YYYY)")
    patient_cpf: str = Field(..., description="CPF do paciente")
    patient_phone: str = Field(..., description="Telefone do paciente")
    doctor_id: str = Field(..., description="ID do médico")
    appointment_date: str = Field(..., description="Data da consulta (YYYY-MM-DD)")
    appointment_time: str = Field(..., description="Horário da consulta (HH:MM)")
    insurance: str = Field(default="particular", description="Convênio ou particular")


class CriarConsultaTool(BaseTool):
    """API para criar agendamento de paciente novo."""
    
    name: str = "criar_consulta_paciente_novo"
    description: str = """
    Cria agendamento para paciente novo.
    IMPORTANTE: Validar dados antes de enviar.
    Explicar ao paciente que é reserva temporária - clínica confirmará.
    """
    args_schema = CriarConsultaInput
    
    def _run(self, **kwargs) -> str:
        """Create new patient appointment."""
        logger.info("Creating appointment", patient=kwargs.get("patient_name"), doctor_id=kwargs.get("doctor_id"))
        
        try:
            # Validações básicas
            required_fields = ["patient_name", "patient_birth", "patient_cpf", "doctor_id", "appointment_date", "appointment_time"]
            missing_fields = [field for field in required_fields if not kwargs.get(field)]
            
            if missing_fields:
                return json.dumps({
                    "success": False,
                    "error": f"Campos obrigatórios faltando: {', '.join(missing_fields)}",
                    "appointment_id": None
                })
            
            # Simular criação do agendamento
            import uuid
            appointment_id = str(uuid.uuid4())[:8]
            
            result = {
                "success": True,
                "appointment_id": appointment_id,
                "status": "reserva_temporaria",
                "message": "Agendamento criado com sucesso! A clínica entrará em contato para confirmação.",
                "details": {
                    "patient": kwargs["patient_name"],
                    "date": kwargs["appointment_date"],
                    "time": kwargs["appointment_time"],
                    "doctor_id": kwargs["doctor_id"],
                    "insurance": kwargs.get("insurance", "particular")
                },
                "next_steps": [
                    "Aguardar confirmação da clínica",
                    "Chegar 15 minutos antes",
                    "Trazer documentos e carteirinha do convênio"
                ]
            }
            
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error("Error creating appointment", error=str(e))
            return json.dumps({
                "success": False,
                "error": f"Erro ao criar agendamento: {str(e)}",
                "appointment_id": None
            })
    
    async def _arun(self, **kwargs) -> str:
        """Async version of appointment creation."""
        return self._run(**kwargs)


class TeleconsultaErnestoInput(BaseModel):
    """Input for Dr. Ernesto online appointments."""
    date: str = Field(..., description="Data no formato YYYY-MM-DD")


class TeleconsultaErnestoTool(BaseTool):
    """API específica para teleconsultas do Dr. Ernesto."""
    
    name: str = "dr_ernesto_online_appointments"
    description: str = """
    Consulta horários específicos de teleconsulta do Dr. Ernesto.
    Apenas Dr. Ernesto oferece teleconsultas.
    """
    args_schema = TeleconsultaErnestoInput
    
    def _run(self, date: str) -> str:
        """Check Dr. Ernesto online availability."""
        logger.info("Checking Dr. Ernesto online slots", date=date)
        
        try:
            # Horários específicos de teleconsulta do Dr. Ernesto
            online_slots = ["10:00:00", "11:00:00", "15:00:00", "16:00:00"]
            
            # Simular disponibilidade
            import random
            available_online = random.sample(online_slots, random.randint(1, 3))
            
            result = {
                "doctor": "Dr. Ernesto Silva",
                "date": date,
                "modality": "teleconsulta",
                "available_slots": [{"start_time": slot, "status": "available", "type": "online"} for slot in available_online],
                "platform": "Google Meet",
                "requirements": [
                    "Conexão estável de internet",
                    "Câmera e microfone funcionando",
                    "Ambiente privado e silencioso"
                ]
            }
            
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error("Error checking online availability", error=str(e))
            return json.dumps({
                "error": f"Erro ao consultar teleconsultas: {str(e)}",
                "available_slots": []
            })
    
    async def _arun(self, date: str) -> str:
        """Async version of online availability check."""
        return self._run(date)