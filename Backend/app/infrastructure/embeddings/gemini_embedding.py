"""Concrete Gemini implementation of EmbeddingProvider."""
from typing import List
from django.conf import settings
import google.generativeai as genai

from Backend.app.application.embedding_provider import EmbeddingProvider

class GeminiEmbeddingProvider(EmbeddingProvider):
    """
    Gera embeddings via Google Gemini usando a biblioteca estável (google.generativeai).
    """

    def __init__(self) -> None:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self._model = settings.EMBEDDING_MODEL

    def embed(self, text: str, task_type: str = "retrieval_document") -> List[float]:
        """Vetoriza um único texto com o task_type informado."""
        
        # Ajusta os task types para os aceitos pela API antiga
        api_task = "retrieval_query" if task_type == "retrieval_query" else "retrieval_document"
        
        try:
            result = genai.embed_content(
                model=self._model,
                content=text,
                task_type=api_task,
            )
            return result['embedding']
        except Exception:
            # Plano B: Caso o Google reclame do prefixo 'models/' na chave dele
            fallback_model = "gemini-embedding-001"
            result = genai.embed_content(
                model=fallback_model,
                content=text,
                task_type=api_task,
            )
            return result['embedding']

    def embed_batch(self, texts: List[str], task_type: str = "retrieval_document") -> List[List[float]]:
        """
        Vetoriza uma lista de textos.
        """
        return [self.embed(t, task_type=task_type) for t in texts]