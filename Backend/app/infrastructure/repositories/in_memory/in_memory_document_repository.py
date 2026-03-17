"""In-memory implementation of DocumentRepository."""
from typing import Dict, List, Optional
from uuid import UUID

from chatbot.domain.entities.document import Document
from chatbot.domain.repositories.document_repository import DocumentRepository


class InMemoryDocumentRepository(DocumentRepository):
    """Stores documents in a plain Python dictionary (no persistence)."""

    def __init__(self) -> None:
        self._store: Dict[UUID, Document] = {}

    def save(self, document: Document) -> None:
        self._store[document.doc_id] = document

    def get_by_id(self, doc_id: UUID) -> Optional[Document]:
        return self._store.get(doc_id)

    def list_all(self) -> List[Document]:
        return list(self._store.values())
