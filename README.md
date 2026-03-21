# 🤖 Chatbot — RAG + Django + Gemini + React

Sistema de chatbot organizado em **monorepo**, com frontend em React, backend em Django REST Framework, autenticação JWT e suporte a **RAG (Retrieval-Augmented Generation)** com a **Gemini API**.

---

## 📋 Sumário

- [Visão Geral](#visão-geral)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [O que cada parte faz](#o-que-cada-parte-faz)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Como o backend funciona](#como-o-backend-funciona)
- [Requisitos](#requisitos)
- [Como rodar o projeto](#como-rodar-o-projeto)
- [Configuração do Django](#configuração-do-django)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
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
| Ponto de entrada | Django CLI | `manage.py` |

---

## Estrutura do Projeto

```text
Chatbot/
├── frontend/                         # Interface web em React
│   ├── public/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   └── admin/
│   │   │       ├── DocumentsList.jsx
│   │   │       ├── DocumentCreate.jsx
│   │   │       ├── DocumentEdit.jsx
│   │   │       └── Categories.jsx
│   │   ├── components/
│   │   │   ├── Layout.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── DocumentForm.jsx
│   │   │   └── ConfirmDialog.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   ├── authService.js
│   │   │   └── documentService.js
│   │   ├── routes/
│   │   │   └── AppRoutes.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── README.md
│
├── Backend/                          # Núcleo do backend
│   ├── __init__.py
│   └── app/
│       ├── __init__.py
│       ├── api/                      # Camada HTTP
│       │   ├── __init__.py
│       │   ├── serializers/
│       │   ├── views/
│       │   │   ├── __init__.py
│       │   │   ├── auth.py
│       │   │   ├── categories.py
│       │   │   ├── chat.py
│       │   │   ├── documents.py
│       │   │   └── users.py
│       │   ├── factories.py
│       │   ├── permissions.py
│       │   └── urls.py
│       │
│       ├── application/              # Casos de uso
│       │   ├── answer_question.py
│       │   ├── create_document.py
│       │   ├── delete_document.py
│       │   ├── embedding_provider.py
│       │   ├── index_document.py
│       │   ├── list_documents.py
│       │   ├── login_admin.py
│       │   ├── update_document.py
│       │   └── vector_store.py
│       │
│       ├── core/
│       │   └── app_settings.py       # Configurações da aplicação
│       │
│       ├── domain/                   # Entidades e contratos
│       │   ├── entities/
│       │   └── repositories/
│       │
│       └── infrastructure/           # Implementações concretas
│           ├── Database/
│           ├── embeddings/
│           ├── indexing/
│           ├── llm/
│           ├── repositories/
│           ├── security/
│           └── vectorstore/
│
├── config/                           # Configuração do Django
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── manage.py                         # Comando principal do Django
├── docs/
│   ├── arquitetura.md
│   ├── backlog.md
│   └── api.md
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── workflows/
├── README.md
└── .gitignore
```

---

## O que cada parte faz

### `frontend/`
Interface do sistema acessada pelo usuário no navegador.

- Telas de login
- Listagem e cadastro de documentos
- Páginas administrativas
- Comunicação com o backend via API

### `Backend/app/api/`
Camada HTTP do backend.

- Recebe requisições
- Valida dados de entrada
- Chama os casos de uso
- Devolve respostas em JSON

Arquivos importantes: `views/`, `serializers/`, `urls.py`, `permissions.py`, `factories.py`

### `Backend/app/application/`
Casos de uso do sistema — define **o que a aplicação faz**:

- Criar, listar, atualizar e deletar documentos
- Responder perguntas
- Indexar conteúdo

> Esta camada não depende diretamente da interface web.

### `Backend/app/domain/`
Camada central da regra de negócio. Contém entidades, contratos de repositório e os conceitos principais do sistema. É a parte mais "pura" da aplicação.

### `Backend/app/infrastructure/`
Implementações concretas dos contratos definidos em `domain/`:

- Conexão com banco de dados
- Autenticação e segurança
- Integração com Gemini
- Embeddings e vector store
- Indexação

### `Backend/app/core/app_settings.py`
Centraliza as configurações da aplicação:

- Chave da API do Gemini
- Modelo de chat e de embeddings
- Valor de `TOP_K`

### `config/`
Configuração do Django: `settings.py`, rotas globais em `urls.py`, e entradas para execução/deploy (`asgi.py`, `wsgi.py`).

### `manage.py`
Ponto de entrada do Django. Usado para rodar o servidor, aplicar migrações, criar superusuário e outros comandos administrativos.

---

## Tecnologias Utilizadas

### Frontend
- React
- JavaScript
- Axios
- React Router

### Backend
- Python
- Django
- Django REST Framework
- Simple JWT
- django-cors-headers

### IA / RAG
- Gemini API
- Embeddings
- Vector Store

---

## Como o backend funciona

A aplicação segue uma arquitetura em camadas:

```
Requisição HTTP
      ↓
   View (api/)
      ↓
 Validação dos dados
      ↓
 Caso de Uso (application/)
      ↓
Entidades + Repositórios + Integrações (domain/ + infrastructure/)
      ↓
   Resposta JSON
```

**Exemplo no chat:**

1. O cliente envia uma pergunta via `POST /api/chat/`
2. A view `chat.py` recebe e valida a entrada
3. O caso de uso processa e monta o prompt
4. A integração com Gemini gera a resposta
5. A API retorna `{ "answer": "..." }`

---

## Requisitos

- Python **3.10+**
- Node.js **18+**
- npm
- Git
- Chave de API do Gemini

---

## Como rodar o projeto

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd Chatbot
```

### 2. Criar e ativar o ambiente virtual

**Windows PowerShell**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows CMD**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Linux / macOS**
```bash
python -m venv .venv
source .venv/bin/activate
```

> Quando ativo, o terminal exibe `(.venv)` no início da linha.

### 3. Instalar dependências do backend

```bash
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers google-genai
```

Para salvar as dependências:

```bash
pip freeze > requirements.txt
```

### 4. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
GEMINI_API_KEY=sua_chave_aqui
CHAT_MODEL=seu_modelo_gemini
EMBEDDING_MODEL=seu_modelo_de_embedding
TOP_K=5
```

### 5. Aplicar migrações

```bash
python manage.py migrate
```

### 6. Criar superusuário

```bash
python manage.py createsuperuser
```

> Usado para acessar `/admin/` e testar geração de tokens JWT.

### 7. Iniciar o servidor backend

```bash
python manage.py runserver
```

O backend ficará disponível em **http://127.0.0.1:8000/**

Para encerrar: `Ctrl + C`

### 8. Rodar o frontend

Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

O frontend ficará disponível em **http://localhost:5173/**

---

## Variáveis de Ambiente

| Variável | Descrição |
|---|---|
| `GEMINI_API_KEY` | Chave de acesso à API do Gemini |
| `CHAT_MODEL` | Modelo usado para gerar respostas |
| `EMBEDDING_MODEL` | Modelo usado para gerar embeddings |
| `TOP_K` | Quantidade de documentos recuperados na busca vetorial |

---

## Configuração do Django

Em `config/settings.py`, certifique-se de que as apps e configurações abaixo estão presentes:

```python
INSTALLED_APPS = [
    ...
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
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
Gera um par de tokens JWT (acesso e refresh).

**Request:**
```json
{
  "username": "seu_usuario",
  "password": "sua_senha"
}
```

**Response:**
```json
{
  "refresh": "...",
  "access": "..."
}
```

---

### `POST /api/token/refresh/`
Renova o token de acesso usando o token de refresh.

**Request:**
```json
{
  "refresh": "seu_refresh_token"
}
```

---

### `POST /api/chat/`
Recebe uma pergunta e retorna a resposta do chatbot.

**Request:**
```json
{
  "question": "O que é RAG?"
}
```

**Response:**
```json
{
  "answer": "RAG é uma abordagem que recupera contexto antes de gerar a resposta."
}
```

---

## Autenticação JWT

1. O usuário realiza login via `POST /api/token/`
2. A API retorna os tokens `access` e `refresh`
3. O token `access` é enviado no header das rotas protegidas:

```http
Authorization: Bearer SEU_TOKEN
```

---

## Testando com Postman

### Gerar token JWT

| Campo | Valor |
|---|---|
| Método | `POST` |
| URL | `http://127.0.0.1:8000/api/token/` |
| Body | `raw → JSON` |

```json
{
  "username": "seu_usuario",
  "password": "sua_senha"
}
```

### Testar o chat

| Campo | Valor |
|---|---|
| Método | `POST` |
| URL | `http://127.0.0.1:8000/api/chat/` |
| Headers | `Content-Type: application/json` |
| Body | `raw → JSON` |

```json
{
  "question": "oi"
}
```

---

## Arquitetura RAG

O projeto está preparado para **RAG (Retrieval-Augmented Generation)**:

```
Pergunta do usuário
        ↓
  Geração de embedding
        ↓
  Busca vetorial (TOP_K documentos)
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
└── infrastructure/
    ├── embeddings/
    └── vectorstore/
```

A integração com o Gemini fica **desacoplada da view**, dentro de `infrastructure/llm/`, o que facilita trocar de provedor, testar e manter o código organizado.

---

## Erros Comuns

### `ECONNREFUSED`
O servidor Django não está rodando.
```bash
python manage.py runserver
```

### `404 Page not found`
A rota não foi registrada. Verifique:
- `config/urls.py`
- `Backend/app/api/urls.py`

### `No module named 'app'`
Problema de import por causa da estrutura de pastas. Certifique-se de que os arquivos `__init__.py` existem em:

```
Backend/
Backend/app/
Backend/app/api/
Backend/app/api/views/
```

### `"O campo 'question' é obrigatório."`
O body não foi enviado corretamente. No Postman: **Body → raw → JSON**

```json
{
  "question": "oi"
}
```

---

## Próximos Passos

- [ ] Integrar a rota `/api/chat/` com o Gemini
- [ ] Ligar o fluxo completo de RAG
- [ ] Proteger rotas administrativas com JWT
- [ ] Conectar o frontend ao login e ao chat
- [ ] Adicionar testes automatizados

---

## ⚡ Resumo Rápido

### Backend
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1       # Windows
# source .venv/bin/activate      # Linux/macOS
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers google-genai
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Teste rápido
```http
POST http://127.0.0.1:8000/api/chat/
Content-Type: application/json

{ "question": "oi" }
```

---

> **Observações:** O backend foi migrado de FastAPI para Django REST Framework. O Django está na raiz através de `manage.py` e `config/`. O código principal da aplicação está em `Backend/app/`. A API do Gemini deve ser configurada via variável de ambiente.
