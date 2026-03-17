"""Abstract repository interface for chat sessions."""
from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from chatbot.domain.entities.message import Message


class ChatRepository(ABC):
    """Defines persistence operations for chat messages."""

    @abstractmethod
    def save_message(self, message: Message) -> None:
        """Persist a message."""

    @abstractmethod
    def get_history(self, session_id: UUID) -> List[Message]:
        """Return all messages belonging to *session_id* ordered by creation time."""

    @abstractmethod
    def clear_history(self, session_id: UUID) -> None:
        """Delete all messages for *session_id*."""
