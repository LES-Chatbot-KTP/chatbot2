"""OpenAI-backed embedding provider."""
from typing import List

from chatbot.application.interfaces.embedding_provider import EmbeddingProvider
from chatbot.config.settings import Settings


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """Generates embeddings using the OpenAI Embeddings API.

    Requires the ``openai`` package and a valid ``OPENAI_API_KEY`` in
    :class:`~chatbot.config.settings.Settings`.
    """

    def __init__(self, settings: Settings) -> None:
        try:
            import openai  # noqa: PLC0415
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "The 'openai' package is required. Install it with: pip install openai"
            ) from exc

        self._client = openai.OpenAI(api_key=settings.openai_api_key)
        self._model = settings.embedding_model

    def embed(self, text: str) -> List[float]:
        """Return the embedding vector for *text*."""
        response = self._client.embeddings.create(input=text, model=self._model)
        return response.data[0].embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Return embedding vectors for a list of texts."""
        response = self._client.embeddings.create(input=texts, model=self._model)
        return [item.embedding for item in response.data]
