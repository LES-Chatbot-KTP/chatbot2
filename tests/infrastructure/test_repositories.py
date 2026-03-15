"""Tests for in-memory repository implementations."""
from uuid import uuid4

import pytest

from chatbot.domain.entities.document import Document
from chatbot.domain.entities.message import Message, Role
from chatbot.infrastructure.repositories.in_memory_chat_repository import (
    InMemoryChatRepository,
)
from chatbot.infrastructure.repositories.in_memory_document_repository import (
    InMemoryDocumentRepository,
)


class TestInMemoryChatRepository:
    def setup_method(self):
        self.repo = InMemoryChatRepository()

    def test_save_and_retrieve_message(self):
        session = uuid4()
        msg = Message(role=Role.USER, content="Hello", session_id=session)
        self.repo.save_message(msg)
        history = self.repo.get_history(session)
        assert len(history) == 1
        assert history[0].content == "Hello"

    def test_empty_history_for_unknown_session(self):
        assert self.repo.get_history(uuid4()) == []

    def test_clear_history(self):
        session = uuid4()
        self.repo.save_message(Message(role=Role.USER, content="Hi", session_id=session))
        self.repo.clear_history(session)
        assert self.repo.get_history(session) == []

    def test_multiple_sessions_isolated(self):
        s1, s2 = uuid4(), uuid4()
        self.repo.save_message(Message(role=Role.USER, content="A", session_id=s1))
        self.repo.save_message(Message(role=Role.USER, content="B", session_id=s2))
        assert len(self.repo.get_history(s1)) == 1
        assert len(self.repo.get_history(s2)) == 1


class TestInMemoryDocumentRepository:
    def setup_method(self):
        self.repo = InMemoryDocumentRepository()

    def test_save_and_get_by_id(self):
        doc = Document(content="Test content")
        self.repo.save(doc)
        retrieved = self.repo.get_by_id(doc.doc_id)
        assert retrieved is not None
        assert retrieved.content == "Test content"

    def test_get_by_unknown_id_returns_none(self):
        assert self.repo.get_by_id(uuid4()) is None

    def test_list_all(self):
        d1 = Document(content="Doc one")
        d2 = Document(content="Doc two")
        self.repo.save(d1)
        self.repo.save(d2)
        all_docs = self.repo.list_all()
        assert len(all_docs) == 2
