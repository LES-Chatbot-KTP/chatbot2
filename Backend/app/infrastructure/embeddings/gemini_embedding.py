"""Concrete Gemini implementation of EmbeddingProvider."""

import google.generativeai as genai
from typing import List
from django.conf import settings
from Backend.app.application.embedding_provider import EmbeddingProvider


class GeminiEmbeddingProvider(EmbeddingProvider):
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self._model = settings.EMBEDDING_MODEL  # "models/text-embedding-004"

    def embed(self, text: str) -> List[float]:
        result = genai.embed_content(
            model=self._model,
            content=text,
            task_type="retrieval_document",
        )
        return result["embedding"]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed(t) for t in texts]