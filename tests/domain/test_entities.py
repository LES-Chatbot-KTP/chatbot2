"""Tests for domain entities."""
import pytest

from chatbot.domain.entities.document import Document
from chatbot.domain.entities.message import Message, Role


class TestMessage:
    def test_create_user_message(self):
        msg = Message(role=Role.USER, content="Hello")
        assert msg.role == Role.USER
        assert msg.content == "Hello"
        assert msg.message_id is not None
        assert msg.session_id is not None

    def test_create_assistant_message(self):
        msg = Message(role=Role.ASSISTANT, content="Hi there")
        assert msg.role == Role.ASSISTANT

    def test_empty_content_raises(self):
        with pytest.raises(ValueError, match="empty"):
            Message(role=Role.USER, content="   ")

    def test_different_messages_have_different_ids(self):
        m1 = Message(role=Role.USER, content="A")
        m2 = Message(role=Role.USER, content="B")
        assert m1.message_id != m2.message_id


class TestDocument:
    def test_create_document(self):
        doc = Document(content="Sample text", source="test")
        assert doc.content == "Sample text"
        assert doc.source == "test"
        assert doc.doc_id is not None

    def test_empty_content_raises(self):
        with pytest.raises(ValueError, match="empty"):
            Document(content="   ")

    def test_metadata_defaults_to_empty_dict(self):
        doc = Document(content="hello")
        assert doc.metadata == {}
