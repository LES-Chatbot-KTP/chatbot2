"""Abstract repository interface for chunk similarity search."""
from abc import ABC, abstractmethod
from typing import List


class ChunkRepository(ABC):

    @abstractmethod
    def buscar_similares(self, query_embedding: List[float], top_k: int) -> List[dict]:
        """
        Retorna os *top_k* chunks mais próximos ao *query_embedding*.

        Cada dict contém:
            - id:             int
            - conteudo:       str
            - documento_nome: str
        """
