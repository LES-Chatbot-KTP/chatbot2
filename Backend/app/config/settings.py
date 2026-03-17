"""Application settings loaded from environment variables."""
import os


class Settings:
    """Central configuration object.

    Values are read from environment variables so that no secrets are
    hard-coded in source code.  Override defaults by setting the
    corresponding environment variable before starting the application.

    Environment variables
    ---------------------
    OPENAI_API_KEY      : OpenAI secret key (required for OpenAI embedding provider).
    EMBEDDING_MODEL     : Name of the OpenAI embedding model.
                          Default: ``text-embedding-3-small``.
    TOP_K               : Number of documents to retrieve per query. Default: ``5``.
    """

    def __init__(self) -> None:
        self.openai_api_key: str = os.environ.get("OPENAI_API_KEY", "")
        self.embedding_model: str = os.environ.get(
            "EMBEDDING_MODEL", "text-embedding-3-small"
        )
        self.top_k: int = int(os.environ.get("TOP_K", "5"))
