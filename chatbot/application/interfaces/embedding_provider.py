"""Abstract interface for embedding providers."""
from abc import ABC, abstractmethod
from typing import List


class EmbeddingProvider(ABC):
    """Generates numerical vector representations (embeddings) for text."""

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Return the embedding vector for *text*."""

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Return embedding vectors for a list of texts."""
