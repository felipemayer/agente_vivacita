# Agente Vivacita - Sistema de Chat AI

Sistema de chat AI para a clínica Vivacita usando FastAPI e CrewAI, integrado com WhatsApp via Evolution API.

## 🚀 Recursos

- **FastAPI**: API moderna e performática
- **CrewAI**: Orquestração de agentes AI especializados
- **WhatsApp Integration**: Via Evolution API compartilhada
- **Roteamento Inteligente**: Distribuição entre Python Chat e N8N
- **Agentes Especializados**: Atendimento médico e escalação
- **Base de Conhecimento**: Informações médicas e da clínica
- **Gestão de Agendamentos**: Integração com sistema existente

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   WhatsApp      │ => │ Webhook Router   │ => │   CrewAI        │
│   (Evolution)   │    │ (Intelligent)    │    │   System        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                         │
                              │                         │
                              v                         v
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Agent Selection │    │ Specialized     │
                       │ - Medical       │    │ Agents          │
                       │ - Scheduling    │    │ - Atendimento   │
                       │ - Emergency     │    │ - Agendamento   │
                       └─────────────────┘    │ - Emergência    │
                                              └─────────────────┘
```

## 🛠️ Tecnologias

- **Backend**: FastAPI, Python 3.11+
- **AI Framework**: CrewAI, OpenRouter (Claude Sonnet 4), OpenAI (Whisper)
- **Database**: Supabase (PostgreSQL)
- **Cache**: Redis
- **Containerização**: Docker, Docker Compose
- **Monitoramento**: Estrutura de logs estruturados

## 📦 Instalação

### Pré-requisitos

- Python 3.11+
- Poetry
- Docker e Docker Compose
- Conta OpenAI com API key
- Evolution API configurada

### Setup Local

1. **Clone e configure o projeto:**
```bash
git clone <repository-url>
cd agente_vivacita
```

2. **Configure variáveis de ambiente:**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. **Instale dependências com Poetry:**
```bash
poetry install
poetry shell
```

4. **Execute com Docker Compose:**
```bash
docker-compose up -d
```

### Configuração de Variáveis

Principais variáveis no arquivo `.env`:

```env
# Aplicação
PROJECT_NAME="Agente Vivacita"
ENVIRONMENT=development
DEBUG=true

# OpenRouter (Claude Sonnet 4)
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# OpenAI (Whisper para áudio)
OPENAI_API_KEY=your_openai_api_key

# Evolution API (WhatsApp)
EVOLUTION_API_URL=https://your-evolution-api.com
EVOLUTION_API_KEY=your_evolution_api_key

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# N8N Integration
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook
N8N_API_KEY=your_n8n_api_key
```

## 🚀 Uso

### Executar Desenvolvimento

```bash
# Com Poetry
poetry run uvicorn src.main:app --reload

# Com Docker
docker-compose up
```

### API Endpoints

- **Health Check**: `GET /health`
- **WhatsApp Webhook**: `POST /api/v1/webhook/whatsapp`
- **Docs**: `http://localhost:8000/docs`

### Roteamento Inteligente

O sistema automaticamente roteia mensagens para agentes especializados:

**Agente de Agendamento** (CrewAI Scheduling):
- Agendamentos: "agendar", "marcar consulta"
- Confirmações: "confirmar", "confirmação"
- Reagendamentos: "remarcar", "trocar horário"
- Cancelamentos: "cancelar", "desmarcar"

**Agente Médico** (CrewAI Medical):
- Dúvidas médicas gerais
- Informações da clínica
- Orientações sobre procedimentos
- Informações sobre especialidades

**Agente de Emergência** (CrewAI Emergency):
- Situações urgentes: "socorro", "emergência"
- Sintomas graves: "dor no peito", "falta de ar"
- Escalação imediata para atendimento humano

## 🧠 Agentes CrewAI

### Agente Médico
- **Função**: Atendimento médico virtual e informações da clínica
- **Ferramentas**: Base de conhecimento médico, informações da clínica
- **Objetivo**: Fornecer informações precisas e orientações médicas

### Agente de Agendamento
- **Função**: Gerenciar agendamentos, confirmações e reagendamentos
- **Ferramentas**: Sistema de agendamento, verificação de disponibilidade
- **Objetivo**: Facilitar o processo de marcação de consultas

### Agente de Emergência
- **Função**: Detectar emergências e escalar imediatamente
- **Análise**: Palavras-chave de urgência, sintomas graves
- **Ação**: Escalação imediata para equipe médica de plantão

## 📊 Monitoramento

### Logs Estruturados
- Requests/responses do WhatsApp
- Decisões de roteamento
- Atividade dos agentes
- Performance das operações

### Métricas
- Taxa de escalação para humanos
- Tempo de resposta dos agentes
- Satisfação do atendimento
- Volume de mensagens por categoria

## 🧪 Testes

```bash
# Executar todos os testes
poetry run pytest

# Testes com coverage
poetry run pytest --cov=src

# Testes específicos
poetry run pytest tests/test_webhook_router.py
```

## 📋 Estrutura do Projeto

```
src/
├── api/                    # FastAPI routes e endpoints
├── agents/                 # CrewAI agents
├── core/                   # Configuração, logging, utilitários
├── integrations/           # WhatsApp, Supabase, N8N
├── models/                 # Pydantic models
├── tools/                  # Ferramentas para os agentes
└── main.py                # Aplicação principal

tests/                      # Testes automatizados
scripts/                    # Scripts utilitários
```

## 🔧 Desenvolvimento

### Adicionando Novos Agentes

1. Criar agente em `src/agents/`
2. Implementar ferramentas necessárias em `src/tools/`
3. Registrar no sistema de roteamento
4. Adicionar testes apropriados

### Padrões de Código

- **Type hints** obrigatórios
- **Logs estruturados** para todas as operações
- **Testes unitários** para lógica de negócio
- **Documentação** inline para funções complexas

## 📈 Roadmap

- [ ] ✅ Setup projeto base
- [ ] 🔄 Implementar webhook router
- [ ] 🔄 Criar agentes médicos
- [ ] ⏳ Integração com Supabase
- [ ] ⏳ Testes E2E
- [ ] ⏳ Deploy em produção

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Projeto proprietário da Clínica Vivacita.

## 📞 Suporte

Para suporte técnico ou dúvidas sobre implementação, consulte a documentação ou entre em contato com a equipe de desenvolvimento.