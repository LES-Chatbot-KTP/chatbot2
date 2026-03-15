# Chatbot

A Python chatbot built with a clean **layered architecture** and **Embeddings-based Retrieval-Augmented Generation (RAG)**.

---

## Architecture Overview

```
chatbot/
├── domain/                   # Core business rules – no external dependencies
│   ├── entities/
│   │   ├── message.py        # Message entity (role, content, session_id, …)
│   │   └── document.py       # Document entity (content, source, metadata, …)
│   └── repositories/
│       ├── chat_repository.py      # Abstract: save/get/clear chat messages
│       └── document_repository.py  # Abstract: save/get/list documents
│
├── application/              # Use cases – orchestrates domain + interfaces
│   ├── interfaces/
│   │   ├── embedding_provider.py   # Abstract: embed(text) → vector
│   │   └── vector_store.py         # Abstract: add_document / search
│   └── use_cases/
│       ├── answer_question.py      # RAG pipeline: embed → search → reply
│       └── index_document.py       # Persist + embed a new document
│
├── infrastructure/           # Concrete implementations of interfaces
│   ├── embeddings/
│   │   └── openai_embedding_provider.py   # OpenAI Embeddings API
│   ├── vector_store/
│   │   └── faiss_vector_store.py          # FAISS flat index (in-process)
│   └── repositories/
│       ├── in_memory_chat_repository.py
│       └── in_memory_document_repository.py
│
├── presentation/             # User-facing adapters
│   └── cli.py                # Interactive REPL
│
└── config/
    └── settings.py           # Environment-variable-based configuration

main.py                       # Wiring / composition root
requirements.txt
tests/
├── domain/           test_entities.py
├── application/      test_use_cases.py
└── infrastructure/   test_repositories.py
```

### Dependency flow

```
Presentation → Application → Domain
Infrastructure implements Application interfaces
```

No layer imports from a layer that is "above" it.

---

## Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your OpenAI API key

```bash
export OPENAI_API_KEY="sk-..."
```

### 3. Run the chatbot

```bash
python main.py
```

### 4. Run the tests

```bash
pytest tests/ -v
```

---

## Configuration

All settings are read from environment variables:

| Variable          | Default                    | Description                        |
|-------------------|----------------------------|------------------------------------|
| `OPENAI_API_KEY`  | *(required)*               | OpenAI secret key                  |
| `EMBEDDING_MODEL` | `text-embedding-3-small`   | OpenAI embedding model name        |
| `TOP_K`           | `5`                        | Number of documents to retrieve    |

---

## CLI Usage

| Input                      | Action                                  |
|----------------------------|-----------------------------------------|
| Any question               | Answer using RAG over indexed documents |
| `/index <text>`            | Embed and index a new piece of knowledge |
| `quit` / `exit` / `q`      | Exit the application                    |
