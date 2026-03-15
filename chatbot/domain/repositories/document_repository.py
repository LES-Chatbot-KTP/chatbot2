"""Abstract repository interface for documents."""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from chatbot.domain.entities.document import Document


class DocumentRepository(ABC):
    """Defines persistence operations for documents."""

    @abstractmethod
    def save(self, document: Document) -> None:
        """Persist a document."""

    @abstractmethod
    def get_by_id(self, doc_id: UUID) -> Optional[Document]:
        """Return a document by its unique identifier."""

    @abstractmethod
    def list_all(self) -> List[Document]:
        """Return all stored documents."""
