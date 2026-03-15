"""Abstract interface for vector store providers."""
from abc import ABC, abstractmethod
from typing import List, Tuple

from chatbot.domain.entities.document import Document


class VectorStore(ABC):
    """Stores document embeddings and supports similarity search."""

    @abstractmethod
    def add_document(self, document: Document, embedding: List[float]) -> None:
        """Index *document* with its pre-computed *embedding*."""

    @abstractmethod
    def search(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[Tuple[Document, float]]:
        """Return the *top_k* most similar documents together with their scores."""

    @abstractmethod
    def clear(self) -> None:
        """Remove all indexed documents."""
