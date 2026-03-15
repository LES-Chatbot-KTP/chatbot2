"""Tests for application use cases using stub implementations."""
from typing import List, Tuple
from uuid import uuid4

import pytest

from chatbot.application.interfaces.embedding_provider import EmbeddingProvider
from chatbot.application.interfaces.vector_store import VectorStore
from chatbot.application.use_cases.answer_question import AnswerQuestion
from chatbot.application.use_cases.index_document import IndexDocument
from chatbot.domain.entities.document import Document
from chatbot.infrastructure.repositories.in_memory_chat_repository import (
    InMemoryChatRepository,
)
from chatbot.infrastructure.repositories.in_memory_document_repository import (
    InMemoryDocumentRepository,
)


# ---------------------------------------------------------------------------
# Stubs / test doubles
# ---------------------------------------------------------------------------

class StubEmbeddingProvider(EmbeddingProvider):
    """Returns a fixed-dimension zero vector for every text."""

    DIM = 4

    def embed(self, text: str) -> List[float]:
        return [0.0] * self.DIM

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed(t) for t in texts]


class StubVectorStore(VectorStore):
    """In-memory vector store that ignores embeddings (returns all docs)."""

    def __init__(self):
        self._documents: List[Document] = []

    def add_document(self, document: Document, embedding: List[float]) -> None:
        self._documents.append(document)

    def search(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[Tuple[Document, float]]:
        return [(doc, 0.0) for doc in self._documents[:top_k]]

    def clear(self) -> None:
        self._documents.clear()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestAnswerQuestion:
    def setup_method(self):
        self.chat_repo = InMemoryChatRepository()
        self.embedding_provider = StubEmbeddingProvider()
        self.vector_store = StubVectorStore()
        self.use_case = AnswerQuestion(
            chat_repository=self.chat_repo,
            embedding_provider=self.embedding_provider,
            vector_store=self.vector_store,
        )

    def test_returns_no_info_message_when_store_empty(self):
        session = uuid4()
        reply = self.use_case.execute(session, "What is AI?")
        assert "could not find" in reply.lower()

    def test_reply_contains_context_when_documents_indexed(self):
        doc = Document(content="AI stands for Artificial Intelligence.")
        self.vector_store.add_document(doc, [0.0] * 4)
        session = uuid4()
        reply = self.use_case.execute(session, "What is AI?")
        assert "Artificial Intelligence" in reply

    def test_saves_user_and_assistant_messages(self):
        session = uuid4()
        self.use_case.execute(session, "Hello")
        history = self.chat_repo.get_history(session)
        assert len(history) == 2  # user + assistant

    def test_get_history_delegates_to_repo(self):
        session = uuid4()
        self.use_case.execute(session, "Hello")
        history = self.use_case.get_history(session)
        assert len(history) == 2


class TestIndexDocument:
    def setup_method(self):
        self.doc_repo = InMemoryDocumentRepository()
        self.embedding_provider = StubEmbeddingProvider()
        self.vector_store = StubVectorStore()
        self.use_case = IndexDocument(
            document_repository=self.doc_repo,
            embedding_provider=self.embedding_provider,
            vector_store=self.vector_store,
        )

    def test_document_persisted_in_repository(self):
        doc = Document(content="Some knowledge")
        self.use_case.execute(doc)
        assert self.doc_repo.get_by_id(doc.doc_id) is not None

    def test_document_added_to_vector_store(self):
        doc = Document(content="Some knowledge")
        self.use_case.execute(doc)
        results = self.vector_store.search([0.0] * 4, top_k=5)
        assert any(d.doc_id == doc.doc_id for d, _ in results)
