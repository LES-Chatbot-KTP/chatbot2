# 🤖 Chatbot — RAG + Django + Gemini + React

Sistema de chatbot organizado em **monorepo**, com frontend em React, backend em Django REST Framework, autenticação JWT, banco de dados **PostgreSQL com pgvector** e suporte a **RAG (Retrieval-Augmented Generation)** com a **Gemini API**.

---

## 📋 Sumário

- [Visão Geral](#visão-geral)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Requisitos](#requisitos)
- [Como rodar o projeto](#como-rodar-o-projeto)
- [Configuração do PostgreSQL + Docker](#configuração-do-postgresql--docker)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Configuração do Django](#configuração-do-django)
- [Rotas da API](#rotas-da-api)
- [Autenticação JWT](#autenticação-jwt)
- [Testando com Postman](#testando-com-postman)
- [Arquitetura RAG](#arquitetura-rag)
- [Erros Comuns](#erros-comuns)
- [Próximos Passos](#próximos-passos)

---

## Visão Geral

Este projeto é organizado como um **monorepo**: frontend e backend ficam no mesmo repositório, mas separados por responsabilidade.

| Parte | Tecnologia | Localização |
|---|---|---|
| Interface web | React + JavaScript | `frontend/` |
| API e chatbot | Python + Django REST Framework | `Backend/` |
| Configuração Django | Django | `config/` |
| Banco de dados | PostgreSQL 16 + pgvector | Docker |
| Ponto de entrada | Django CLI | `manage.py` |

---

## Estrutura do Projeto

```
Chatbot/
├── frontend/                         # Interface web em React
│   └── src/
│       ├── pages/
│       ├── components/
│       ├── services/
│       └── routes/
│
├── Backend/
│   └── app/
│       ├── api/                      # Views, serializers, URLs
│       ├── application/              # Casos de uso
│       ├── core/
│       ├── domain/                   # Entidades e contratos
│       ├── infrastructure/           # Gemini, embeddings, vectorstore
│       └── documents/                # Models e indexação de PDFs
│           ├── models.py
│           ├── apps.py
│           └── management/commands/
│               └── indexar_documentos.py
│
├── config/                           # Configuração do Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── Documentos/                       # PDFs indexados no banco
│   ├── portarias/
│   ├── resolucoes/
│   └── rod/
│
├── migrations/
│   └── criar_indice_vetorial.sql     # Índice vetorial no PostgreSQL
│
├── docker-compose.yml                # PostgreSQL + pgvector via Docker
├── Dockerfile                        # Imagem do backend
├── init.sql                          # Habilita extensão pgvector
├── .env.example                      # Modelo de variáveis de ambiente
├── manage.py
└── requirements.txt
```

---

## Tecnologias Utilizadas

### Frontend
- React, JavaScript, Axios, React Router

### Backend
- Python, Django, Django REST Framework, Simple JWT, django-cors-headers

### Banco de Dados
- PostgreSQL 16 + pgvector (via Docker)
- psycopg2-binary (driver Python)

### IA / RAG
- Gemini API, Embeddings, Vector Store (pgvector)

---

## Requisitos

- Python 3.10+
- Node.js 18+
- Docker Desktop
- Chave de API do Gemini

---

## Como rodar o projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/LES-Chatbot-KTP/Chatbot.git
cd Chatbot
```

### 2. Criar e ativar o ambiente virtual

**Windows PowerShell**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependências do backend

```bash
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers google-genai psycopg2-binary pypdf python-dotenv
```

### 4. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Edite o .env e preencha GEMINI_API_KEY, POSTGRES_PASSWORD e SECRET_KEY
```

### 5. Subir o banco de dados

> O Docker Desktop precisa estar aberto antes desse passo.

```bash
docker-compose up -d db
```

### 6. Aplicar migrações

```bash
python manage.py makemigrations documents
python manage.py migrate
```

### 7. Criar o índice vetorial no PostgreSQL

**Windows PowerShell:**
```powershell
Get-Content migrations/criar_indice_vetorial.sql | docker exec -i chatbot_db psql -U chatbot_user -d chatbot
```

**Linux / macOS:**
```bash
docker exec -i chatbot_db psql -U chatbot_user -d chatbot < migrations/criar_indice_vetorial.sql
```

### 8. Indexar os documentos PDF

```bash
python manage.py indexar_documentos
```

Resultado esperado:
```
✅ Indexação concluída: 42 documento(s), 650 chunk(s)
```

### 9. Criar superusuário e iniciar o servidor

```bash
python manage.py createsuperuser
python manage.py runserver
```

O backend ficará disponível em **http://127.0.0.1:8000/**

### 10. Rodar o frontend

Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

O frontend ficará disponível em **http://localhost:5173/**

---

## Configuração do PostgreSQL + Docker

O projeto usa **PostgreSQL 16 com a extensão pgvector** para armazenar os documentos e seus embeddings vetoriais.

### Estrutura do banco

| Tabela | Descrição |
|---|---|
| `documents_documento` | Armazena os 42 PDFs (portarias, resoluções, RODs) |
| `documents_chunkdocumento` | Armazena os chunks de texto e embeddings vetoriais |

### Verificar se o banco está rodando

```bash
docker-compose ps
# chatbot_db   Up (healthy)   0.0.0.0:5432->5432/tcp
```

### Consultar dados no banco

```bash
docker exec -it chatbot_db psql -U chatbot_user -d chatbot
```

```sql
-- Documentos por tipo
SELECT tipo, COUNT(*) FROM documents_documento GROUP BY tipo;

-- Total de chunks
SELECT COUNT(*) FROM documents_chunkdocumento;
```

---

## Variáveis de Ambiente

Crie um arquivo `.env` na raiz baseado no `.env.example`:

| Variável | Descrição |
|---|---|
| `GEMINI_API_KEY` | Chave de acesso à API do Gemini |
| `CHAT_MODEL` | Modelo para gerar respostas (ex: gemini-1.5-flash) |
| `EMBEDDING_MODEL` | Modelo para embeddings (ex: models/text-embedding-004) |
| `TOP_K` | Quantidade de chunks recuperados na busca vetorial |
| `POSTGRES_DB` | Nome do banco de dados |
| `POSTGRES_USER` | Usuário do banco |
| `POSTGRES_PASSWORD` | Senha do banco |
| `DB_HOST` | Host do banco (localhost em dev, db no Docker) |
| `SECRET_KEY` | Chave secreta do Django |
| `DEBUG` | True em desenvolvimento, False em produção |

> ⚠️ Nunca suba o `.env` para o GitHub. Apenas o `.env.example`.

---

## Configuração do Django

Em `config/settings.py`:

```python
INSTALLED_APPS = [
    ...
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "Backend.app",
    "Backend.app.documents",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]
```

---

## Rotas da API

### `POST /api/token/`
Gera tokens JWT de acesso e refresh.

```json
// Request
{ "username": "seu_usuario", "password": "sua_senha" }

// Response
{ "refresh": "...", "access": "..." }
```

### `POST /api/token/refresh/`
Renova o token de acesso.

```json
{ "refresh": "seu_refresh_token" }
```

### `POST /api/chat/`
Recebe uma pergunta e retorna a resposta do chatbot.

```json
// Request
{ "question": "O que é RAG?" }

// Response
{ "answer": "RAG é uma abordagem que recupera contexto antes de gerar a resposta." }
```

---

## Autenticação JWT

1. Login via `POST /api/token/`
2. Usar o token `access` no header das rotas protegidas:

```http
Authorization: Bearer SEU_TOKEN
```

---

## Testando com Postman

| Campo | Valor |
|---|---|
| Método | `POST` |
| URL | `http://127.0.0.1:8000/api/chat/` |
| Headers | `Content-Type: application/json` |
| Body | `raw → JSON` |

```json
{ "question": "oi" }
```

---

## Arquitetura RAG

```
Pergunta do usuário
        ↓
  Geração de embedding (Gemini)
        ↓
  Busca vetorial no PostgreSQL (TOP_K chunks)
        ↓
  Contexto + Pergunta → Prompt
        ↓
     Gemini API
        ↓
  Resposta contextualizada
```

Arquivos envolvidos:

```
Backend/app/
├── application/
│   ├── embedding_provider.py
│   ├── vector_store.py
│   └── index_document.py
├── infrastructure/
│   ├── embeddings/
│   ├── vectorstore/
│   └── llm/
└── documents/
    └── management/commands/
        └── indexar_documentos.py
```

---

## Erros Comuns

### `open //./pipe/dockerDesktopLinuxEngine`
O Docker Desktop não está aberto. Abra-o e aguarde inicializar.

### `No module named 'psycopg2'`
```bash
pip install psycopg2-binary
```

### `No module named 'dotenv'`
```bash
pip install python-dotenv
```

### `No installed app with label 'documents'`
Certifique-se de que `"Backend.app.documents"` está em `INSTALLED_APPS` e que o arquivo `apps.py` existe em `Backend/app/documents/`.

### `Operador '<' reservado` (PowerShell)
Use `Get-Content` no lugar de `<`:
```powershell
Get-Content arquivo.sql | docker exec -i chatbot_db psql -U chatbot_user -d chatbot
```

### `404 Not Found` nas rotas
Verifique `config/urls.py` e `Backend/app/api/urls.py`.

---

## Próximos Passos

- [ ] Gerar embeddings via Gemini e popular a coluna `embedding_vector`
- [ ] Implementar o fluxo RAG completo na rota `/api/chat/`
- [ ] Proteger rotas administrativas com JWT
- [ ] Conectar o frontend ao login e ao chat
- [ ] Adicionar testes automatizados
- [ ] Dashboard de métricas e relatórios

---

## ⚡ Resumo Rápido

```bash
# 1. Ambiente
python -m venv .venv && .venv\Scripts\Activate.ps1
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers google-genai psycopg2-binary pypdf python-dotenv

# 2. Banco (Docker Desktop aberto)
cp .env.example .env
docker-compose up -d db

# 3. Migrações e índice vetorial
python manage.py makemigrations documents
python manage.py migrate
Get-Content migrations/criar_indice_vetorial.sql | docker exec -i chatbot_db psql -U chatbot_user -d chatbot

# 4. Indexar PDFs
python manage.py indexar_documentos

# 5. Servidor
python manage.py createsuperuser
python manage.py runserver

# 6. Frontend (outro terminal)
cd frontend && npm install && npm run dev
```

> **Observações:** O banco SQLite foi substituído por PostgreSQL via Docker. Os 42 documentos PDF estão indexados em 650 chunks. O Django está na raiz via `manage.py` e `config/`. A API do Gemini deve ser configurada via variável de ambiente.
