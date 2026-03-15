"""Domain entity representing a chat message."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class Role(str, Enum):
    """Role of the participant in a conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message:
    """A single message within a chat session."""

    role: Role
    content: str
    session_id: UUID = field(default_factory=uuid4)
    message_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("Message content must not be empty.")
