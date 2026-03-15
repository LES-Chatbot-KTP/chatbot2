"""Domain entity representing an indexed document."""
from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Document:
    """A piece of text content that can be embedded and retrieved."""

    content: str
    source: str = ""
    doc_id: UUID = field(default_factory=uuid4)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("Document content must not be empty.")
