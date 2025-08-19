# Projeto Sistema de Chat WhatsApp com Python + CrewAI
# Foco: Migração Gradual - Chat AI System

**Version**: 2.0  
**Date**: August 18, 2025  
**Escopo**: Sistema de Chat AI isolado (mantendo N8N para sync, confirmação e reagendamento)

---

## 1. Visão Geral do Projeto

### 1.1 Objetivo
Criar um sistema de chat AI independente em Python + CrewAI para substituir apenas o workflow "CHAT" do N8N, mantendo todos os outros workflows (sync, confirmação, reagendamento) funcionando no N8N.

### 1.2 Estratégia de Migração Gradual
```yaml
fase_1_chat_system:
  escopo: Sistema de Chat AI standalone
  mantem_no_n8n:
    - sync: Sincronização Konsist (24 nodes)
    - confirmacao: Confirmação de consultas (15 nodes) 
    - reagendar: Reagendamento de consultas (15 nodes)
    - base_conhecimento: Knowledge base (19 nodes)
    - acorda_supabase: Database keepalive (4 nodes)
  
  migra_para_python:
    - chat: Sistema de Chat AI (65 nodes) ✅
    - message_processing: Processamento de mensagens WhatsApp
    - human_escalation: Escalação para humanos
    - conversation_management: Gerenciamento de conversas
```

### 1.3 Benefícios da Abordagem Gradual
- **Risco Reduzido**: Mantém sistemas críticos funcionando
- **Teste Isolado**: Chat pode ser testado independentemente
- **Aprendizado**: Equipe ganha experiência com nova arquitetura
- **Rollback Simples**: Fácil retorno ao N8N se necessário

---

## 2. Arquitetura do Sistema de Chat

### 2.1 Arquitetura Simplificada

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WhatsApp      │    │   N8N Workflows │    │   Databases     │
│   (Evolution)   │    │   (Mantidos)    │    │   (Existentes)  │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │                      │                      │
    ┌─────▼──────────────────────▼──────────────────────▼─────┐
    │              Webhook Router                             │
    │         (Determina: Chat vs N8N)                       │
    └─────────────┬─────────────────────┬─────────────────────┘
                  │                     │
         ┌────────▼──────────┐  ┌──────▼──────────┐
         │  Python Chat      │  │  N8N Workflows  │``
         │  System           │  │  (Existentes)   │
         │                   │  │                 │
         │ ┌───────────────┐ │  │ • Sync          │
         │ │ CrewAI        │ │  │ • Confirmação   │
         │ │ Multi-Agent   │ │  │ • Reagendamento │
         │ └───────────────┘ │  │ • Knowledge     │
         │                   │  └─────────────────┘
         └───────────────────┘
```

### 2.2 Componentes Principais

#### 2.2.1 Webhook Router (Novo)
```python
# Determinador inteligente de rota
webhook_router:
  funcao: Analisar mensagens e decidir destino
  criterios:
    - chat_conversation: Python System
    - appointment_booking: N8N
    - confirmation_response: N8N  
    - rescheduling_request: N8N
```

#### 2.2.2 Python Chat System (Novo)
```python
chat_system:
  componentes:
    - message_processor: Processamento de mensagens
    - crewai_engine: Motor de AI multi-agent
    - conversation_manager: Gerenciamento de contexto
    - escalation_handler: Escalação para humanos
    - whatsapp_client: Interface com Evolution API
```

#### 2.2.3 Integrações Mantidas
```python
integracoes_existentes:
  databases:
    - supabase: Mantém estrutura atual
    - postgresql: Memory e chat histories
  
  apis_externas:
    - evolution_api: WhatsApp (compartilhado)
    - konsist_api: Usado apenas pelo N8N
    - openai_api: Usado pelo Python Chat
    - google_drive: Usado apenas pelo N8N
```

---

## 3. Estrutura do Projeto

### 3.1 Estrutura de Diretórios

```
whatsapp-chat-system/
├── src/
│   ├── api/                    # FastAPI application
│   │   ├── main.py            # App principal
│   │   ├── routers/           # Routers da API
│   │   │   ├── webhook.py     # Webhook router principal
│   │   │   ├── chat.py        # Endpoints de chat
│   │   │   └── health.py      # Health checks
│   │   └── middleware/        # Middleware customizado
│   ├── core/                   # Core business logic
│   │   ├── chat/              # Sistema de chat
│   │   │   ├── processor.py   # Processador de mensagens
│   │   │   ├── manager.py     # Gerenciador de conversas
│   │   │   └── escalation.py  # Sistema de escalação
│   │   ├── crewai/            # Integração CrewAI
│   │   │   ├── agents.py      # Definições de agents
│   │   │   ├── tasks.py       # Definições de tasks
│   │   │   └── crews.py       # Configuração de crews
│   │   └── routing/           # Sistema de roteamento
│   │       └── webhook_router.py
│   ├── integrations/          # Integrações externas
│   │   ├── whatsapp/          # Evolution API
│   │   ├── database/          # Supabase/PostgreSQL
│   │   └── n8n/               # Interface com N8N (se necessário)
│   ├── models/                # Modelos de dados
│   │   ├── chat.py           # Modelos de chat
│   │   └── message.py        # Modelos de mensagem
│   └── utils/                 # Utilitários
├── crews/                     # Definições CrewAI
│   ├── medical_chat/          # Crew principal de chat médico
│   │   ├── agents.py         # Agents especializados
│   │   ├── tasks.py          # Tasks do workflow
│   │   └── crew_config.py    # Configuração do crew
│   └── tools/                 # Tools customizados
├── tests/                     # Testes
├── docker/                    # Configurações Docker
├── docs/                      # Documentação
└── scripts/                   # Scripts de deploy e utilidades
```

### 3.2 Configuração Inicial

#### 3.2.1 pyproject.toml
```toml
[tool.poetry]
name = "whatsapp-chat-system"
version = "0.1.0"
description = "Sistema de Chat AI para WhatsApp com CrewAI"
authors = ["Equipe Vivacitá <dev@vivacita.com>"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = "^0.24.0"
crewai = "^0.67.0"
langchain = "^0.1.0"
langchain-openai = "^0.1.0"
openai = "^1.0.0"
httpx = "^0.25.0"
pydantic = "^2.0.0"
sqlalchemy = "^2.0.0"
asyncpg = "^0.29.0"
redis = "^5.0.0"
supabase = "^2.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
black = "^23.0.0"
ruff = "^0.1.0"
mypy = "^1.7.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

#### 3.2.2 Dockerfile Simples
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy Poetry files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

# Copy application
COPY src/ ./src/
COPY langflow/ ./langflow/

# Expose port
EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 4. Implementação Core

### 4.1 Webhook Router Principal

```python
# src/core/routing/webhook_router.py
"""
Router inteligente para determinar se mensagem vai para Python Chat ou N8N
"""
from typing import Dict, Any, Tuple
import re
import logging

class WebhookRouter:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Padrões que indicam necessidade de N8N (agendamento/confirmação)
        self.n8n_patterns = [
            r'\b(agendar|consulta|marcar)\b',
            r'\b(confirmar|confirmação)\b', 
            r'\b(reagendar|remarcar)\b',
            r'\b(cancelar|cancelamento)\b',
            r'\b(disponibilidade|agenda)\b'
        ]
        
        # Padrões que indicam chat geral (Python)
        self.chat_patterns = [
            r'\b(olá|oi|bom dia|boa tarde|boa noite)\b',
            r'\b(ajuda|dúvida|informação)\b',
            r'\b(como|onde|quando|porque)\b',
            r'\b(falar com|atendente|pessoa)\b'
        ]
    
    async def route_message(self, message_data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Determina se mensagem deve ir para Python Chat ou N8N
        
        Returns:
            Tuple[str, Dict]: ("python_chat" | "n8n", message_data_with_routing)
        """
        message_text = message_data.get('body', '').lower()
        phone = message_data.get('from', '')
        
        # Enriquecer dados da mensagem
        enriched_data = {
            **message_data,
            'routing': {
                'timestamp': message_data.get('timestamp'),
                'phone': phone,
                'message_length': len(message_text),
                'has_media': message_data.get('type') != 'text'
            }
        }
        
        # Verificar se é uma conversa ativa no Python Chat
        if await self._has_active_chat_conversation(phone):
            self.logger.info(f"Routing to Python Chat - Active conversation: {phone}")
            return "python_chat", enriched_data
        
        # Análise de padrões para determinar rota
        n8n_score = self._calculate_pattern_score(message_text, self.n8n_patterns)
        chat_score = self._calculate_pattern_score(message_text, self.chat_patterns)
        
        # Lógica de decisão
        if n8n_score > chat_score and n8n_score > 0.3:
            route = "n8n"
            enriched_data['routing']['reason'] = 'appointment_related'
            enriched_data['routing']['confidence'] = n8n_score
        else:
            route = "python_chat"
            enriched_data['routing']['reason'] = 'general_chat'
            enriched_data['routing']['confidence'] = chat_score
        
        self.logger.info(
            f"Routing decision: {route} (n8n_score: {n8n_score:.2f}, chat_score: {chat_score:.2f})"
        )
        
        return route, enriched_data
    
    def _calculate_pattern_score(self, text: str, patterns: list) -> float:
        """Calcula score baseado nos padrões encontrados"""
        matches = 0
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches += 1
        
        return matches / len(patterns) if patterns else 0.0
    
    async def _has_active_chat_conversation(self, phone: str) -> bool:
        """Verifica se existe conversa ativa no sistema de chat Python"""
        # Implementar verificação no banco de dados
        # Por enquanto, retorna False (todas as mensagens passam pela análise)
        return False
```

### 4.2 Sistema de Chat Principal

```python
# src/core/chat/processor.py
"""
Processador principal de mensagens de chat
"""
from typing import Dict, Any, Optional
import asyncio
import logging
from datetime import datetime

from src.core.crewai.crews import MedicalChatCrew
from src.core.chat.manager import ConversationManager
from src.core.chat.escalation import EscalationHandler
from src.integrations.whatsapp.client import WhatsAppClient

class ChatProcessor:
    def __init__(self):
        self.medical_crew = MedicalChatCrew()
        self.conversation_manager = ConversationManager()
        self.escalation_handler = EscalationHandler()
        self.whatsapp_client = WhatsAppClient()
        self.logger = logging.getLogger(__name__)
    
    async def process_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa mensagem de chat completa"""
        phone = message_data.get('from')
        message_text = message_data.get('body', '')
        message_type = message_data.get('type', 'text')
        
        try:
            # 1. Gerenciar conversa
            conversation = await self.conversation_manager.get_or_create_conversation(phone)
            
            # 2. Processar diferentes tipos de mídia
            processed_content = await self._process_message_content(message_data)
            
            # 3. Verificar necessidade de escalação antes do AI
            if await self.escalation_handler.should_escalate_immediately(processed_content):
                return await self._handle_immediate_escalation(conversation, processed_content)
            
            # 4. Processar com AI (CrewAI)
            ai_response = await self._process_with_ai(conversation, processed_content)
            
            # 5. Verificar se AI recomenda escalação
            if ai_response.get('escalation_needed', False):
                return await self._handle_ai_escalation(conversation, ai_response)
            
            # 6. Enviar resposta via WhatsApp
            whatsapp_response = await self._send_whatsapp_response(phone, ai_response)
            
            # 7. Salvar interação na conversa
            await self.conversation_manager.save_interaction(
                conversation['id'], 
                processed_content, 
                ai_response,
                whatsapp_response
            )
            
            return {
                'status': 'success',
                'conversation_id': conversation['id'],
                'ai_response': ai_response,
                'whatsapp_message_id': whatsapp_response.get('messageId'),
                'processing_time': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing chat message: {e}")
            
            # Resposta de fallback
            fallback_response = await self._send_fallback_response(phone)
            
            return {
                'status': 'error',
                'error': str(e),
                'fallback_sent': True,
                'whatsapp_message_id': fallback_response.get('messageId')
            }
    
    async def _process_message_content(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa conteúdo da mensagem baseado no tipo"""
        message_type = message_data.get('type', 'text')
        
        if message_type == 'text':
            return {
                'type': 'text',
                'content': message_data.get('body', ''),
                'original_message': message_data
            }
        
        elif message_type == 'audio':
            # Transcrever áudio com Whisper
            audio_url = message_data.get('media_url')
            transcription = await self._transcribe_audio(audio_url)
            
            return {
                'type': 'audio',
                'content': transcription,
                'audio_url': audio_url,
                'original_message': message_data
            }
        
        elif message_type == 'image':
            # Analisar imagem com GPT-4 Vision
            image_url = message_data.get('media_url')
            image_description = await self._analyze_image(image_url)
            
            return {
                'type': 'image', 
                'content': image_description,
                'image_url': image_url,
                'original_message': message_data
            }
        
        else:
            return {
                'type': 'unsupported',
                'content': f"Tipo de mensagem não suportado: {message_type}",
                'original_message': message_data
            }
    
    async def _process_with_ai(self, conversation: Dict, content: Dict) -> Dict[str, Any]:
        """Processa mensagem com CrewAI"""
        
        # Preparar contexto da conversa
        conversation_history = await self.conversation_manager.get_conversation_history(
            conversation['id'], 
            limit=10
        )
        
        # Preparar input para CrewAI
        crew_input = {
            'message': content['content'],
            'message_type': content['type'],
            'patient_phone': conversation['patient_phone'],
            'conversation_history': conversation_history,
            'metadata': {
                'conversation_id': conversation['id'],
                'timestamp': datetime.utcnow().isoformat()
            }
        }
        
        # Executar crew médico
        ai_result = await self.medical_crew.process_medical_query(crew_input)
        
        return {
            'response_text': ai_result.get('response', ''),
            'confidence': ai_result.get('confidence', 0.8),
            'tools_used': ai_result.get('tools_used', []),
            'escalation_needed': ai_result.get('escalation_needed', False),
            'escalation_reason': ai_result.get('escalation_reason'),
            'metadata': ai_result.get('metadata', {})
        }
    
    async def _send_whatsapp_response(self, phone: str, ai_response: Dict) -> Dict[str, Any]:
        """Envia resposta via WhatsApp"""
        response_text = ai_response.get('response_text', '')
        
        if not response_text:
            response_text = "Desculpe, não consegui processar sua mensagem. Um atendente entrará em contato."
        
        return await self.whatsapp_client.send_text_message(
            phone=phone,
            message=response_text
        )
    
    async def _handle_immediate_escalation(self, conversation: Dict, content: Dict) -> Dict[str, Any]:
        """Lida com escalação imediata (emergências)"""
        escalation_result = await self.escalation_handler.escalate_conversation(
            conversation['id'],
            reason="immediate_escalation",
            trigger_content=content['content']
        )
        
        # Enviar mensagem de escalação
        escalation_message = (
            "Detectei que você precisa de atendimento prioritário. "
            "Um profissional entrará em contato com você em breve. "
            "Em caso de emergência, ligue para 192 (SAMU) ou procure o hospital mais próximo."
        )
        
        whatsapp_response = await self.whatsapp_client.send_text_message(
            phone=conversation['patient_phone'],
            message=escalation_message
        )
        
        return {
            'status': 'escalated_immediately',
            'escalation_id': escalation_result['escalation_id'],
            'whatsapp_message_id': whatsapp_response.get('messageId')
        }
    
    async def _handle_ai_escalation(self, conversation: Dict, ai_response: Dict) -> Dict[str, Any]:
        """Lida com escalação recomendada pela AI"""
        escalation_result = await self.escalation_handler.escalate_conversation(
            conversation['id'],
            reason=ai_response.get('escalation_reason', 'ai_recommendation'),
            trigger_content=ai_response.get('response_text', '')
        )
        
        # Enviar resposta da AI + notificação de escalação
        full_message = ai_response.get('response_text', '') + "\n\nUm atendente humano também foi notificado para auxiliá-lo."
        
        whatsapp_response = await self.whatsapp_client.send_text_message(
            phone=conversation['patient_phone'],
            message=full_message
        )
        
        return {
            'status': 'escalated_by_ai',
            'escalation_id': escalation_result['escalation_id'],
            'ai_response': ai_response,
            'whatsapp_message_id': whatsapp_response.get('messageId')
        }
    
    async def _send_fallback_response(self, phone: str) -> Dict[str, Any]:
        """Envia resposta de fallback em caso de erro"""
        fallback_message = (
            "Desculpe, estou enfrentando dificuldades técnicas no momento. "
            "Um atendente humano entrará em contato com você em breve."
        )
        
        return await self.whatsapp_client.send_text_message(
            phone=phone,
            message=fallback_message
        )
    
    async def _transcribe_audio(self, audio_url: str) -> str:
        """Transcreve áudio usando Whisper"""
        # Implementar transcrição com OpenAI Whisper
        # Por enquanto, retorna placeholder
        return "[Áudio transcrito - implementar Whisper]"
    
    async def _analyze_image(self, image_url: str) -> str:
        """Analisa imagem usando GPT-4 Vision"""
        # Implementar análise com GPT-4 Vision
        # Por enquanto, retorna placeholder
        return "[Imagem analisada - implementar GPT-4 Vision]"
```

### 4.3 CrewAI Medical Chat System

```python
# src/core/crewai/crews.py
"""
CrewAI Medical Chat System - Crew principal para chat médico
"""
import asyncio
from typing import Dict, Any, List
import logging

from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from src.core.crewai.agents import create_medical_agents
from src.core.crewai.tasks import create_medical_tasks
from src.core.config import get_settings

class MedicalChatCrew:
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        
        # Configurar LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            openai_api_key=self.settings.openai_api_key
        )
        
        # Criar agents
        self.agents = create_medical_agents(self.llm)
        
        # Criar crew
        self.crew = Crew(
            agents=list(self.agents.values()),
            verbose=True,
            memory=True,
            planning=True
        )
    
    async def process_medical_query(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa consulta médica usando crew multi-agent"""
        
        try:
            # Extrair informações do input
            message = input_data.get('message', '')
            message_type = input_data.get('message_type', 'text')
            conversation_history = input_data.get('conversation_history', [])
            
            # Criar tasks dinâmicas baseadas no input
            tasks = create_medical_tasks(
                message=message,
                message_type=message_type,
                conversation_history=conversation_history,
                agents=self.agents
            )
            
            # Executar crew
            result = await self._execute_crew_async(tasks, input_data)
            
            # Processar resultado
            return self._process_crew_result(result, input_data)
            
        except Exception as e:
            self.logger.error(f"CrewAI processing error: {e}")
            return self._create_fallback_response("CrewAI Error")
    
    async def _execute_crew_async(self, tasks: List[Task], input_data: Dict) -> Any:
        """Executa crew de forma assíncrona"""
        
        # Atualizar crew com tasks específicas
        crew_with_tasks = Crew(
            agents=list(self.agents.values()),
            tasks=tasks,
            verbose=True,
            memory=True,
            planning=True
        )
        
        # Executar em thread separada para não bloquear
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            crew_with_tasks.kickoff
        )
    
    def _process_crew_result(self, crew_result: Any, input_data: Dict) -> Dict[str, Any]:
        """Processa resultado do crew para formato padronizado"""
        
        # Extrair resposta final
        if hasattr(crew_result, 'tasks_output') and crew_result.tasks_output:
            # Última task contém a resposta final
            final_task_output = crew_result.tasks_output[-1]
            response_text = final_task_output.result if hasattr(final_task_output, 'result') else str(final_task_output)
        else:
            response_text = str(crew_result)
        
        # Analisar necessidade de escalação
        escalation_needed = self._detect_escalation_in_response(response_text, input_data)
        
        # Extrair metadados das tasks
        tools_used = []
        if hasattr(crew_result, 'tasks_output'):
            for task_output in crew_result.tasks_output:
                if hasattr(task_output, 'agent') and hasattr(task_output.agent, 'role'):
                    tools_used.append(task_output.agent.role)
        
        return {
            'response': response_text,
            'confidence': 0.8,  # CrewAI não fornece confidence diretamente
            'tools_used': tools_used,
            'escalation_needed': escalation_needed,
            'escalation_reason': self._get_escalation_reason(response_text),
            'crew_execution_details': {
                'agents_used': [agent.role for agent in self.agents.values()],
                'tasks_completed': len(crew_result.tasks_output) if hasattr(crew_result, 'tasks_output') else 0
            }
        }
    
    def _detect_escalation_in_response(self, response_text: str, input_data: Dict) -> bool:
        """Detecta se resposta indica necessidade de escalação"""
        
        escalation_indicators = [
            "falar com atendente",
            "não consegui resolver",
            "situação complexa", 
            "procure ajuda médica",
            "emergência",
            "urgente",
            "precisa de avaliação presencial",
            "consulte um médico",
            "atendimento especializado"
        ]
        
        response_lower = response_text.lower()
        return any(indicator in response_lower for indicator in escalation_indicators)
    
    def _get_escalation_reason(self, response_text: str) -> str:
        """Determina razão específica da escalação"""
        response_lower = response_text.lower()
        
        if any(word in response_lower for word in ["emergência", "urgente", "grave"]):
            return "emergency"
        elif any(word in response_lower for word in ["complexa", "especializado"]):
            return "complex_case"
        elif any(word in response_lower for word in ["presencial", "consulte"]):
            return "requires_physical_exam"
        else:
            return "general_escalation"
    
    def _create_fallback_response(self, error_type: str) -> Dict[str, Any]:
        """Cria resposta de fallback em caso de erro"""
        return {
            'response': (
                "Desculpe, estou enfrentando dificuldades técnicas no momento. "
                "Um atendente humano será notificado para auxiliá-lo."
            ),
            'confidence': 0.0,
            'tools_used': [],
            'escalation_needed': True,
            'escalation_reason': f'technical_error_{error_type.lower()}',
            'error': error_type
        }
```

```python
# src/core/crewai/agents.py
"""
Definições de agents especializados para chat médico
"""
from crewai import Agent
from langchain_openai import ChatOpenAI
from typing import Dict

def create_medical_agents(llm: ChatOpenAI) -> Dict[str, Agent]:
    """Cria agents especializados para chat médico"""
    
    # Agent Principal - Triagem e Atendimento
    triage_agent = Agent(
        role='Assistente de Triagem Médica',
        goal='Realizar triagem inicial de sintomas e orientar pacientes adequadamente',
        backstory="""Você é um assistente especializado em triagem médica da Clínica Vivacitá.
        Sua função é fazer a primeira avaliação dos sintomas relatados pelos pacientes,
        orientar sobre cuidados básicos e determinar a urgência do atendimento.""",
        llm=llm,
        verbose=True,
        allow_delegation=True
    )
    
    # Agent Especialista - Conhecimento Médico
    medical_expert = Agent(
        role='Especialista em Informações Médicas',
        goal='Fornecer informações médicas precisas e orientações baseadas em evidências',
        backstory="""Você é um especialista em medicina geral com vasto conhecimento
        sobre sintomas, condições médicas e tratamentos. Você fornece informações
        precisas e baseadas em evidências, sempre priorizando a segurança do paciente.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Agent de Escalação - Determina necessidade de atendimento humano
    escalation_agent = Agent(
        role='Especialista em Escalação',
        goal='Avaliar quando um caso precisa ser encaminhado para atendimento humano',
        backstory="""Você é responsável por avaliar a complexidade dos casos e determinar
        quando um paciente precisa falar com um atendente humano ou médico. Você considera
        fatores como gravidade dos sintomas, complexidade do caso e limitações da assistência virtual.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Agent de Comunicação - Formata respostas para pacientes
    communication_agent = Agent(
        role='Especialista em Comunicação com Pacientes',
        goal='Formatar respostas de forma clara, empática e adequada para WhatsApp',
        backstory="""Você é especialista em comunicação médica, responsável por
        transformar informações técnicas em linguagem acessível e empática para pacientes.
        Você adapta a comunicação para o formato WhatsApp, sendo claro e acolhedor.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    return {
        'triage': triage_agent,
        'medical_expert': medical_expert,
        'escalation': escalation_agent,
        'communication': communication_agent
    }
```

```python
# src/core/crewai/tasks.py
"""
Definições de tasks para workflow de chat médico
"""
from crewai import Task
from typing import Dict, List, Any

def create_medical_tasks(
    message: str, 
    message_type: str,
    conversation_history: List[Dict],
    agents: Dict
) -> List[Task]:
    """Cria tasks específicas baseadas no input do paciente"""
    
    # Contexto da conversa
    history_context = ""
    if conversation_history:
        history_context = "\n".join([
            f"- {msg.get('role', 'user')}: {msg.get('content', '')}" 
            for msg in conversation_history[-5:]  # Últimas 5 mensagens
        ])
    
    # Task 1: Triagem Inicial
    triage_task = Task(
        description=f"""
        Analise a mensagem do paciente e realize a triagem inicial:
        
        Mensagem: "{message}"
        Tipo: {message_type}
        
        Histórico da conversa:
        {history_context}
        
        Avalie:
        1. Principais sintomas ou preocupações mencionadas
        2. Grau de urgência (baixo, médio, alto, emergência)
        3. Se há informações suficientes para orientação
        4. Se precisa de mais esclarecimentos
        
        Forneça uma avaliação estruturada da situação do paciente.
        """,
        expected_output="Avaliação de triagem com grau de urgência e principais pontos identificados",
        agent=agents['triage']
    )
    
    # Task 2: Consulta Especializada
    expert_task = Task(
        description="""
        Com base na triagem realizada, forneça orientações médicas apropriadas:
        
        1. Informações sobre os sintomas ou condições identificadas
        2. Orientações de cuidados que o paciente pode tomar
        3. Sinais de alerta que requerem atenção imediata
        4. Recomendações sobre quando procurar atendimento presencial
        
        Base suas orientações em evidências médicas e diretrizes clínicas.
        """,
        expected_output="Orientações médicas detalhadas e baseadas em evidências",
        agent=agents['medical_expert'],
        context=[triage_task]
    )
    
    # Task 3: Avaliação de Escalação
    escalation_task = Task(
        description="""
        Avalie se este caso precisa ser encaminhado para atendimento humano:
        
        Considere:
        1. Gravidade dos sintomas identificados
        2. Complexidade do caso médico
        3. Necessidade de exame físico ou diagnóstico especializado
        4. Limitações da assistência virtual
        5. Preferência do paciente por atendimento humano
        
        Determine: ESCALAR ou NÃO ESCALAR
        Se escalar, forneça a razão específica.
        """,
        expected_output="Decisão de escalação (SIM/NÃO) com justificativa",
        agent=agents['escalation'],
        context=[triage_task, expert_task]
    )
    
    # Task 4: Comunicação Final
    communication_task = Task(
        description="""
        Formule a resposta final para o paciente de forma clara e empática:
        
        1. Use linguagem acessível e não técnica
        2. Seja empático e acolhedor
        3. Formate adequadamente para WhatsApp (parágrafos curtos)
        4. Inclua orientações práticas e próximos passos
        5. Se houver escalação, explique de forma tranquilizadora
        
        A resposta deve ser completa, útil e transmitir confiança.
        """,
        expected_output="Resposta final formatada e pronta para envio via WhatsApp",
        agent=agents['communication'],
        context=[triage_task, expert_task, escalation_task]
    )
    
    return [triage_task, expert_task, escalation_task, communication_task]
```

---

## 5. API e Rotas

### 5.1 API Principal

```python
# src/api/main.py
"""
FastAPI application principal
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.api.routers import webhook, chat, health
from src.core.config import get_settings

def create_app() -> FastAPI:
    settings = get_settings()
    
    app = FastAPI(
        title="WhatsApp Chat System",
        description="Sistema de Chat AI para WhatsApp - Clínica Vivacitá",
        version="1.0.0"
    )
    
    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configurar apropriadamente em produção
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Routers
    app.include_router(webhook.router, prefix="/api/v1/webhook", tags=["Webhook"])
    app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
    app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
    
    @app.get("/")
    async def root():
        return {
            "service": "WhatsApp Chat System",
            "version": "1.0.0",
            "status": "running"
        }
    
    return app

app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0", 
        port=8000,
        reload=settings.debug
    )
```

### 5.2 Webhook Router

```python
# src/api/routers/webhook.py
"""
Router principal para webhooks do WhatsApp
"""
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from typing import Dict, Any
import logging
import httpx

from src.core.routing.webhook_router import WebhookRouter
from src.core.chat.processor import ChatProcessor

router = APIRouter()
logger = logging.getLogger(__name__)

webhook_router = WebhookRouter()
chat_processor = ChatProcessor()

@router.post("/whatsapp")
async def handle_whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Webhook principal para mensagens do WhatsApp
    Decide se encaminha para Python Chat ou N8N
    """
    try:
        # Receber dados do webhook
        message_data = await request.json()
        
        logger.info(f"Received WhatsApp message: {message_data.get('from')} - {message_data.get('type')}")
        
        # Determinar rota (Python Chat vs N8N)
        route, enriched_data = await webhook_router.route_message(message_data)
        
        if route == "python_chat":
            # Processar com sistema Python Chat
            background_tasks.add_task(
                process_chat_message_async,
                enriched_data
            )
            
            return {
                "status": "accepted",
                "route": "python_chat",
                "message_id": enriched_data.get('messageId'),
                "processing": "async"
            }
        
        elif route == "n8n":
            # Encaminhar para N8N
            n8n_response = await forward_to_n8n(enriched_data)
            
            return {
                "status": "forwarded", 
                "route": "n8n",
                "n8n_response": n8n_response
            }
        
        else:
            raise HTTPException(status_code=500, detail="Invalid routing decision")
            
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_chat_message_async(message_data: Dict[str, Any]):
    """Processa mensagem de chat de forma assíncrona"""
    try:
        result = await chat_processor.process_message(message_data)
        logger.info(f"Chat message processed: {result.get('status')}")
    except Exception as e:
        logger.error(f"Async chat processing error: {e}")

async def forward_to_n8n(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """Encaminha mensagem para N8N existente"""
    
    # URL do webhook N8N existente
    n8n_webhook_url = "https://your-n8n-instance.com/webhook/whatsapp"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                n8n_webhook_url,
                json=message_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return {"status": "success", "n8n_response": response.json()}
            else:
                logger.error(f"N8N forwarding failed: {response.text}")
                return {"status": "error", "error": response.text}
                
    except Exception as e:
        logger.error(f"N8N forwarding error: {e}")
        return {"status": "error", "error": str(e)}

@router.get("/routing-stats")
async def get_routing_stats():
    """Estatísticas de roteamento para monitoramento"""
    # Implementar estatísticas básicas
    return {
        "total_messages": 0,
        "python_chat_routes": 0,
        "n8n_routes": 0,
        "error_routes": 0
    }
```

---

## 6. Configuração e Deploy

### 6.1 Configuração

```python
# src/core/config.py
"""
Configuração da aplicação
"""
from pydantic import BaseSettings, Field
from typing import Optional

class Settings(BaseSettings):
    # App
    app_name: str = "WhatsApp Chat System"
    debug: bool = Field(False, env="DEBUG")
    
    # Database (usar mesmas do N8N)
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_key: str = Field(..., env="SUPABASE_KEY")
    postgresql_url: str = Field(..., env="POSTGRESQL_URL")
    
    # APIs Externas
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    evolution_api_url: str = Field(..., env="EVOLUTION_API_URL")
    evolution_api_key: str = Field(..., env="EVOLUTION_API_KEY")
    
    # CrewAI Settings
    crewai_verbose: bool = Field(True, env="CREWAI_VERBOSE")
    crewai_memory: bool = Field(True, env="CREWAI_MEMORY")
    
    # N8N (para encaminhamento)
    n8n_webhook_url: str = Field(..., env="N8N_WEBHOOK_URL")
    
    class Config:
        env_file = ".env"

def get_settings() -> Settings:
    return Settings()
```

### 6.2 Docker Compose para Desenvolvimento

```yaml
# docker-compose.yml
version: '3.8'

services:
  chat-system:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=true
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - POSTGRESQL_URL=${POSTGRESQL_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - EVOLUTION_API_URL=${EVOLUTION_API_URL}
      - EVOLUTION_API_KEY=${EVOLUTION_API_KEY}
      - CREWAI_VERBOSE=true
      - CREWAI_MEMORY=true
      - N8N_WEBHOOK_URL=${N8N_WEBHOOK_URL}
    volumes:
      - ./src:/app/src
      - ./crews:/app/crews
```

---

## 7. Estratégia de Implantação

### 7.1 Fases de Implementação

#### Fase 1: Setup Base (Semana 1)
```yaml
objetivos:
  - Setup do projeto Python + LangFlow
  - Configuração do ambiente de desenvolvimento
  - Implementação do webhook router básico
  - Conexão com databases existentes

entregaveis:
  - Projeto estruturado funcionando
  - LangFlow rodando localmente
  - Webhook router respondendo
  - Conectividade com Supabase/PostgreSQL
```

#### Fase 2: Sistema de Chat (Semana 2-3)
```yaml
objetivos:
  - Implementação do ChatProcessor
  - Integração com LangFlow AI
  - Sistema de escalação básico
  - Testes de integração

entregaveis:
  - Chat AI funcionando com LangFlow
  - Processamento de texto, áudio e imagem
  - Escalação para humanos
  - Testes unitários e de integração
```

#### Fase 3: Integração e Testes (Semana 4)
```yaml
objetivos:
  - Integração completa com WhatsApp
  - Testes de carga
  - Refinamento do roteamento
  - Monitoramento e logging

entregaveis:
  - Sistema completo integrado
  - Métricas e monitoramento
  - Documentação técnica
  - Ambiente de staging funcionando
```

### 7.2 Estratégia de Deploy Gradual

```yaml
deploy_strategy:
  ambiente_teste:
    - Deploy em ambiente separado
    - Configurar webhook de teste no WhatsApp
    - Testes com números específicos
    - Validação com equipe interna
  
  deploy_produção:
    fase_1:
      - Deploy em produção (paralelo ao N8N)
      - Configurar roteamento conservador (80% N8N, 20% Python)
      - Monitoramento intensivo
      - Rollback imediato se problemas
    
    fase_2:
      - Aumentar gradualmente tráfego para Python (50/50)
      - Validar performance e estabilidade
      - Ajustar algoritmo de roteamento
    
    fase_3:
      - Roteamento inteligente completo
      - N8N apenas para agendamentos específicos
      - Python Chat para conversas gerais
```

---

## 8. Monitoramento e Observabilidade

### 8.1 Métricas Essenciais

```python
# Métricas a acompanhar
metricas_principais:
  performance:
    - tempo_resposta_chat: <3 segundos
    - tempo_langflow: <5 segundos
    - disponibilidade: >99%
  
  qualidade:
    - taxa_escalacao: <20%
    - satisfacao_usuarios: >4.0/5.0
    - precisao_roteamento: >95%
  
  volume:
    - mensagens_por_hora: tracking
    - conversas_ativas: tracking
    - distribuicao_python_vs_n8n: tracking
```

### 8.2 Alertas Críticos

```python
alertas_criticos:
  sistema:
    - api_down: notificacao_imediata
    - langflow_down: notificacao_imediata
    - database_error: notificacao_imediata
  
  qualidade:
    - taxa_escalacao_alta: >30% em 1h
    - tempo_resposta_alto: >10s por 5min
    - erro_rate_alto: >5% em 15min
```

---

## 9. Próximos Passos

### 9.1 Ações Imediatas

```bash
# 1. Setup do projeto
mkdir whatsapp-chat-system
cd whatsapp-chat-system
poetry init

# 2. Instalar dependências
poetry add fastapi uvicorn crewai langchain langchain-openai openai httpx

# 3. Criar estrutura
mkdir -p src/{api,core,integrations,models}
mkdir -p crews/{medical_chat,tools}

# 4. Configurar ambiente
cp .env.example .env
# Editar .env com credenciais

# 5. Executar setup inicial
docker-compose up -d
```

### 9.2 Sequência de Desenvolvimento

1. **Semana 1**: Setup + Webhook Router
2. **Semana 2**: Sistema de Chat + CrewAI
3. **Semana 3**: Integração WhatsApp + Escalação
4. **Semana 4**: Testes + Deploy Staging
5. **Semana 5**: Deploy Produção Gradual

### 9.3 Critérios de Sucesso

```yaml
criterios_sucesso:
  tecnico:
    - Sistema responde em <3s
    - Zero downtime durante migração
    - Roteamento >95% preciso
  
  negocio:
    - Pacientes não percebem mudança
    - Equipe consegue gerenciar escalações
    - Custo operacional reduzido
  
  qualidade:
    - Testes automatizados >80% coverage
    - Documentação completa
    - Monitoramento em tempo real
```

---

## 10. Resumo Executivo

Este projeto foca na migração **gradual e segura** apenas do sistema de Chat AI, mantendo todos os outros workflows funcionando perfeitamente no N8N. 

### Benefícios Principais:
- **Risco Mínimo**: Mantém sistemas críticos inalterados
- **Aprendizado Incremental**: Equipe ganha experiência gradualmente  
- **Fallback Simples**: Pode voltar ao N8N facilmente
- **Teste Isolado**: Chat pode ser validado independentemente

### Timeline: 5 semanas
### Escopo: Apenas Chat AI System
### Estratégia: Coexistência inteligente Python + N8N

**Resultado**: Sistema de chat mais inteligente, escalável e manutenível, sem impactar operações críticas existentes.

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"id": "1", "content": "Analyze existing project structure and N8N workflows", "status": "completed"}, {"id": "2", "content": "Create comprehensive PRD document", "status": "completed"}, {"id": "3", "content": "Design system architecture for Python/LangFlow implementation", "status": "completed"}, {"id": "4", "content": "Document migration strategy from N8N to Python", "status": "completed"}, {"id": "5", "content": "Create focused project initialization guide for Chat-first migration", "status": "completed"}]