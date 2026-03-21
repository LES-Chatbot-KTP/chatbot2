"""Application settings loaded from environment variables."""
import os


class Settings:
    """Central configuration object.

    Environment variables
    ---------------------
    GEMINI_API_KEY   : Gemini API key.
    CHAT_MODEL       : Gemini model used for chat/generation.
                       Default: ``gemini-2.5-flash``.
    EMBEDDING_MODEL  : Gemini embedding model.
                       Default: ``gemini-embedding-001``.
    TOP_K            : Number of documents to retrieve per query.
                       Default: ``5``.
    """

    def __init__(self) -> None:
        self.gemini_api_key: str = os.environ.get("GEMINI_API_KEY", "")
        self.chat_model: str = os.environ.get("CHAT_MODEL", "gemini-2.5-flash")
        self.embedding_model: str = os.environ.get(
            "EMBEDDING_MODEL", "gemini-embedding-001"
        )
        self.top_k: int = int(os.environ.get("TOP_K", "5"))