"""FAISS-backed in-process vector store."""
from typing import List, Tuple

from chatbot.application.interfaces.vector_store import VectorStore
from chatbot.domain.entities.document import Document


class FaissVectorStore(VectorStore):
    """Stores document embeddings in a FAISS flat index (in memory).

    Requires the ``faiss-cpu`` package:

    .. code-block:: bash

        pip install faiss-cpu
    """

    def __init__(self) -> None:
        try:
            import faiss  # noqa: PLC0415
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "The 'faiss-cpu' package is required. Install it with: "
                "pip install faiss-cpu"
            ) from exc

        self._faiss = faiss
        self._index = None  # lazily initialised on first add_document call
        self._documents: List[Document] = []

    # ------------------------------------------------------------------
    # VectorStore interface
    # ------------------------------------------------------------------

    def add_document(self, document: Document, embedding: List[float]) -> None:
        """Index *document* with its pre-computed *embedding*."""
        import numpy as np  # noqa: PLC0415

        vector = np.array([embedding], dtype="float32")
        if self._index is None:
            dim = vector.shape[1]
            self._index = self._faiss.IndexFlatL2(dim)
        self._index.add(vector)
        self._documents.append(document)

    def search(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[Tuple[Document, float]]:
        """Return the *top_k* most similar documents and their L2 distances."""
        import numpy as np  # noqa: PLC0415

        if self._index is None or not self._documents:
            return []

        k = min(top_k, len(self._documents))
        query = np.array([query_embedding], dtype="float32")
        distances, indices = self._index.search(query, k)

        results: List[Tuple[Document, float]] = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1:
                results.append((self._documents[idx], float(dist)))
        return results

    def clear(self) -> None:
        """Remove all indexed documents and reset the FAISS index."""
        self._index = None
        self._documents.clear()
