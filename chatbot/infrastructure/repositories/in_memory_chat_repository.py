"""In-memory implementation of ChatRepository."""
from collections import defaultdict
from typing import List
from uuid import UUID

from chatbot.domain.entities.message import Message
from chatbot.domain.repositories.chat_repository import ChatRepository


class InMemoryChatRepository(ChatRepository):
    """Stores messages in a plain Python dictionary (no persistence)."""

    def __init__(self) -> None:
        self._store: dict = defaultdict(list)

    def save_message(self, message: Message) -> None:
        self._store[message.session_id].append(message)

    def get_history(self, session_id: UUID) -> List[Message]:
        return list(self._store[session_id])

    def clear_history(self, session_id: UUID) -> None:
        self._store.pop(session_id, None)
