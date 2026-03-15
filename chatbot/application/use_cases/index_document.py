"""Use case: embed and index a document so it can be retrieved later."""
from chatbot.application.interfaces.embedding_provider import EmbeddingProvider
from chatbot.application.interfaces.vector_store import VectorStore
from chatbot.domain.entities.document import Document
from chatbot.domain.repositories.document_repository import DocumentRepository


class IndexDocument:
    """
    Orchestrates document indexing:

    1. Persist the raw document via the document repository.
    2. Compute the document embedding.
    3. Store the embedding in the vector store.
    """

    def __init__(
        self,
        document_repository: DocumentRepository,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ) -> None:
        self._doc_repo = document_repository
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store

    def execute(self, document: Document) -> None:
        """Persist and index *document*."""
        self._doc_repo.save(document)
        embedding = self._embedding_provider.embed(document.content)
        self._vector_store.add_document(document, embedding)
