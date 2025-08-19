# Checklist - Sistema de Atendimento Vivacità Saúde Mental
# Status do Projeto: Sistema Python + CrewAI em Desenvolvimento

## ✅ STATUS ATUAL - IMPLEMENTADO

### 🏗️ ESTRUTURA DO PROJETO (COMPLETO)
- [x] **Estrutura base Python** com Poetry e FastAPI ✅
- [x] **Docker** setup completo com docker-compose ✅
- [x] **Configuração** de variáveis de ambiente (.env) ✅
- [x] **Logging** estruturado implementado ✅
- [x] **API base** com endpoints de health ✅

### 🔀 SISTEMA DE ROTEAMENTO (COMPLETO)
- [x] **WebhookRouter** inteligente implementado ✅
- [x] **Análise de padrões** para diferentes tipos de conversa ✅
- [x] **Roteamento CrewAI**:
  - [x] Emergency escalation (emergências)
  - [x] Medical consultation (dúvidas gerais)
  - [x] Appointment workflows (agendamentos/confirmações)
- [x] **Sistema de scoring** para determinação de rota ✅
- [x] **Detecção de emergência** com escalação imediata ✅

### 🤖 AGENTES CREWAI (IMPLEMENTADO PARCIAL)
- [x] **Hígia Agent** (Assistente principal) implementado ✅
- [x] **Medical Crew** com workflow sequencial ✅
- [x] **Tools médicas** básicas implementadas ✅
- [x] **Configuração OpenAI** integrada ✅

### 📡 INTEGRAÇÕES (IMPLEMENTADO PARCIAL)
- [x] **WhatsApp Client** base implementado ✅
- [x] **Audio processing** com Whisper integrado ✅
- [x] **Chat processor** core implementado ✅

---

## 🚧 EM DESENVOLVIMENTO (Tasks do Archon)

### 📱 TRATAMENTO COMPLETO DE MENSAGENS
- [x] **Webhook de entrada** configurado para receber mensagens do WhatsApp
- [x] **Identificação do tipo de mensagem**:
  - [x] Texto (conversation) ✅
  - [x] Áudio (audioMessage) ✅ com Whisper
  - [ ] Imagem (imageMessage) ⏳ Em desenvolvimento
- [x] **Extração de dados básicos**:
  - [x] Número do remetente ✅
  - [x] Nome do contato (pushName) ✅
  - [x] ID da instância ✅
  - [x] Timestamp da mensagem ✅
  - [x] Status fromMe (mensagem própria vs cliente) ✅

### 🔄 PROCESSAMENTO POR TIPO DE CONTEÚDO
- [x] **Mensagens de Texto**: Processamento direto ✅
- [x] **Mensagens de Áudio**:
  - [x] Conversão para arquivo MP3 ✅
  - [x] Transcrição usando OpenAI Whisper ✅
  - [x] Conversão do áudio transcrito para texto ✅
- [ ] **Mensagens de Imagem**:
  - [ ] Download da imagem via URL direta ⏳
  - [ ] Análise com GPT-4 Vision ⏳
  - [ ] Integração no contexto da conversa ⏳

### 🤖 SISTEMA DE IA - HÍGIA (EVOLUTIVO)
- [x] **Modelo**: GPT-4o mini (OpenAI) ✅
- [ ] **Memória**: PostgreSQL Chat Memory ⏳ Precisa implementar
- [ ] **Base de conhecimento**: Supabase Vector Store ⏳ Configurar
- [x] **Personalidade**: Hígia - assistente empática ✅

### 🛠️ FERRAMENTAS DE IA (EM DESENVOLVIMENTO)
- [x] **base_de_conhecimento**: RAG básico ✅
- [ ] **lista_medicos**: Lista médicos ativos ⏳
- [ ] **disponibilidade_agenda_medico**: Consulta horários ⏳
- [ ] **criar_consulta_paciente_novo**: Agendamentos ⏳
- [ ] **buscar_paciente**: Busca por telefone ⏳

---

## ⏳ PENDENTE DE DESENVOLVIMENTO

### 🕐 CONTROLE DE FILA E TIMING (TODO)
- [ ] **Fila de mensagens** no Supabase para agrupamento ⏳
- [ ] **Wait de 5 segundos** antes do processamento ⏳
- [ ] **Verificação de última mensagem** para evitar duplicatas ⏳
- [ ] **Concatenação automática** de mensagens sequenciais ⏳
- [ ] **Limpeza da fila** após processamento ⏳

### ⏰ VALIDAÇÕES TEMPORAIS (TODO)
- [ ] **Horário mínimo**: Agendamentos com 2h de antecedência ⏳
- [ ] **Data/hora atual**: Implementar validações temporais ⏳
- [ ] **Funcionamento**: 8h-12h e 14h-18h ⏳

### 👥 HUMAN-IN-THE-LOOP (PLANEJADO)
- [x] **Sistema de escalação** básico implementado ✅
- [ ] **Detecção de mensagens do atendente** (fromMe = true) ⏳
- [ ] **Registro temporal** da última intervenção humana ⏳
- [ ] **Bloqueio da IA** por 10 minutos após intervenção humana ⏳
- [ ] **Limpeza automática** de registros antigos ⏳
- [ ] **Inserção de mensagens humanas** na memória do chat ⏳

## 📋 REGRAS DE NEGÓCIO - AGENDAMENTOS

### Validações Obrigatórias
- [ ] **Data >= hoje** (nunca datas passadas)
- [ ] **Horário para hoje**: >= agora + 2h
- [ ] **Horários válidos**: 08:00-12:00 ou 14:00-18:00
- [ ] **Doctor_id correto** via lista_medicos
- [ ] **Usar apenas** horários de `available_slots`

### Fluxo de Agendamento
1. [ ] **Identificação da necessidade**:
   - [ ] Tipo: Psiquiatria/Psicologia/Neuropsicológica
   - [ ] Idade do paciente
   - [ ] Modalidade: Presencial/Teleconsulta
   - [ ] Urgência

2. [ ] **Coleta de dados obrigatórios**:
   - [ ] Nome completo
   - [ ] Data de nascimento
   - [ ] Convênio
   - [ ] CPF
   - [ ] Endereço com CEP
   - [ ] Documentos (RG + carteirinha)

3. [ ] **Consulta de disponibilidade**:
   - [ ] Obter doctor_id via lista_medicos
   - [ ] Consultar disponibilidade_agenda_medico
   - [ ] Filtrar horários válidos para hoje
   - [ ] Oferecer apenas available_slots

4. [ ] **Criação do agendamento**:
   - [ ] Validar dados antes da API
   - [ ] Usar criar_consulta_paciente_novo
   - [ ] Explicar: "Reserva temporária"

### Tratamento de Erros da API
- [ ] **Análise de dados enviados** em caso de erro
- [ ] **Diagnóstico automático**:
  - [ ] Data passada
  - [ ] Horário muito próximo
  - [ ] Médico inválido
  - [ ] Horário fora do funcionamento
- [ ] **Resposta empática** explicando o problema
- [ ] **Oferecimento de alternativas** automaticamente

## 💰 VALORES E SERVIÇOS

### Consultas
- [ ] **Psiquiátrica**: R$ 500,00 à vista
- [ ] **Psicoterapia**: R$ 250,00 à vista / R$ 150,00 (Bradesco)
- [ ] **Laudos**: R$ 500,00 à vista

### Avaliações
- [ ] **Neuropsicológica**: R$ 1.950,00 à vista / R$ 2.100,00 (4x)
- [ ] **Psicológica**: R$ 1.350,00 à vista / R$ 1.450,00 (4x)
- [ ] **Sessões**: Semanais, 5-10 sessões total

### Formas de Pagamento
- [ ] PIX
- [ ] Cartão (crédito/débito)
- [ ] Dinheiro

## 🩺 ESPECIALIDADES E MÉDICOS

### Dr. Ernesto (Características Especiais)
- [ ] **Único para crianças** (7+ anos)
- [ ] **Laudos médicos**
- [ ] **Teleconsultas**
- [ ] **API específica** para agendamentos online

### Políticas Especiais
- [ ] **NÃO existe "retorno gratuito"**
- [ ] **Até 15 dias**: "nova consulta com desconto"
- [ ] **Após 15 dias**: consulta integral
- [ ] **NUNCA usar** a palavra "retorno"

## 🚨 PROTOCOLO DE EMERGÊNCIA

### Palavras-chave de Alerta
- [ ] Suicídio
- [ ] Desespero
- [ ] Autolesão
- [ ] "Não aguento mais"

### Ações Obrigatórias
- [ ] **Consultar** "Hígia - RAG - Diretrizes de Atendimento"
- [ ] **Transferir imediatamente** para equipe médica
- [ ] **Manter tom empático** durante transferência

## 🗃️ SISTEMA DE DADOS

### Supabase - Tabelas
- [ ] **n8n_chat_histories**: Histórico de conversas
- [ ] **fila_mensagens**: Controle de agrupamento
- [ ] **human_in_loop**: Controle de intervenção humana
- [ ] **images**: Armazenamento de imagens enviadas
- [ ] **documents**: Base de conhecimento (RAG)

### Google Drive
- [ ] **Upload automático** de imagens
- [ ] **Nomenclatura**: `{nome}_{timestamp}.{ext}`
- [ ] **Pasta específica** para organização

## ⚙️ CONFIGURAÇÕES TÉCNICAS

### APIs Externas
- [ ] **OpenAI**: GPT-4o + Whisper + Embeddings
- [ ] **Vivacità API**: Médicos, agendamentos, disponibilidade
- [ ] **WhatsApp Evolution API**: Envio/recebimento mensagens
- [ ] **Google Drive API**: Upload de arquivos

### Credenciais Necessárias
- [ ] OpenAI API Key
- [ ] Supabase API Key
- [ ] PostgreSQL Connection
- [ ] Google Drive OAuth2
- [ ] Vivacità API Token
- [ ] WhatsApp Instance Token

## 📊 MONITORAMENTO E LOGS

### Logs de Sistema
- [ ] **Estrutura do webhook** para debug
- [ ] **Tipos de mensagem** processados
- [ ] **Erros de API** com diagnóstico
- [ ] **Transferências humanas** com timestamp

### Métricas de Controle
- [ ] **Tempo de resposta** da IA
- [ ] **Taxa de sucesso** de agendamentos
- [ ] **Intervenções humanas** por período
- [ ] **Tipos de erro** mais frequentes

## ✅ CHECKLIST PRÉ-RESPOSTA

### Para Agendamentos
- [ ] Consultei lista_medicos para obter doctor_id?
- [ ] Consultei API de disponibilidade com doctor_id correto?
- [ ] Ofereci apenas horários de available_slots?
- [ ] Filtrei horários válidos para hoje (>= agora + 2h)?
- [ ] Confirmei o nome do médico com o paciente?

### Para Situações Críticas
- [ ] Identifiquei palavras de emergência?
- [ ] Consultei RAG apropriado?
- [ ] Escalei para equipe médica?
- [ ] Mantive tom empático?

---

## 📊 ANÁLISE DE PROGRESSO - TASKS DO ARCHON

### ✅ TAREFAS CONCLUÍDAS
1. **Setup projeto Python base** - ✅ COMPLETO (Task: 83138618-28a9-430b-832b-dbd1fcc8d4e3)
2. **Webhook Router inteligente** - ✅ COMPLETO (Task: 0e753c9c-7821-4f19-b8c7-b229e8cbbf5e)
3. **Estrutura FastAPI + CrewAI** - ✅ COMPLETO
4. **Configuração de ambiente** - ✅ COMPLETO
5. **Agente Hígia básico** - ✅ IMPLEMENTADO

### 🔄 EM PROGRESSO (Status: review)
1. **Setup projeto base** - Review pendente (Task status: review)
2. **Webhook Router** - Implementado, aguardando validação (Task status: review)

### ⏳ PRÓXIMAS TAREFAS PRIORITÁRIAS
1. **Configurar tokens OpenAI** (Task: e44b3ceb-d12c-4035-86ae-50ce040be7e3) - Status: todo
2. **Criar Medical Chat Agent** (Task: 153862a4-5d94-4631-9132-9c67f29521ac) - Status: todo  
3. **Implementar Escalation Agent** (Task: f8233fcf-4688-45bd-99e2-f90c8fe324c9) - Status: todo
4. **Definir Tasks médicas** (Task: 2044e67e-2756-4850-b7c2-5a90fc10e30f) - Status: todo

### 📝 TAREFAS PENDENTES (Longo Prazo)
- Configurar Evolution API WhatsApp (Task: 3bab9e4d-1d9d-4f54-99f2-3ed02e33db51)
- Implementar sistema de escalação (Task: cf3c310c-2ced-4d36-a3c4-df55914470f0) 
- Sistema de monitoramento (Task: 1e904bfe-b939-44f7-8a08-fcba70b60b46)
- Suite de testes (Task: a7fe4b22-033e-4984-bd99-d9dac3290a49)
- Deploy staging (Task: b548df1f-3adf-4a80-90f7-e6986e5ce3be)
- Deploy produção (Task: 0f4428b9-1e34-496f-9974-d1f7d043ad41)

---

## 🎯 OBJETIVOS DO SISTEMA

1. **Atendimento 24/7** via WhatsApp ✅ Estrutura base pronta
2. **Processamento multi-modal** (texto ✅, voz ✅, imagem ⏳)
3. **Agendamentos automatizados** ⏳ Em desenvolvimento  
4. **Transferência inteligente** ✅ Sistema de escalação básico
5. **Prevenção de spam** ⏳ Controle de fila pendente
6. **Protocolo de emergência** ✅ Detecção implementada
7. **Base de conhecimento** ⏳ RAG básico implementado

---

## 🚀 RECOMENDAÇÕES PRÓXIMOS PASSOS

### PRIORIDADE ALTA (Esta Semana)
1. **Configurar credenciais OpenAI/Evolution API** - Bloqueia testes
2. **Validar Webhook Router** - Testar roteamento em ambiente real
3. **Implementar Medical Agent completo** - Core do sistema

### PRIORIDADE MÉDIA (Próximas 2 semanas)  
1. **Escalation Agent e Crew** - Sistema de transferência humana
2. **Tools médicas específicas** - Agendamento, busca de pacientes
3. **Sistema de memória** - PostgreSQL Chat Memory

### PRIORIDADE BAIXA (Futuro)
1. **Sistema anti-spam** - Otimização de performance
2. **Monitoramento completo** - Observabilidade
3. **Deploy estratégico** - Produção gradual

**Status Geral: ~35% Implementado** 
- Estrutura base: ✅ 100%
- Core AI System: ✅ 60% 
- Integrações: ⏳ 30%
- Testes/Deploy: ⏳ 0%