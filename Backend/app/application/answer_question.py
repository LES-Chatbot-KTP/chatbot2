"""Use case: answer a user question using context retrieved from the vector store."""
from typing import List
from uuid import UUID

from chatbot.application.interfaces.embedding_provider import EmbeddingProvider
from chatbot.application.interfaces.vector_store import VectorStore
from chatbot.domain.entities.message import Message, Role
from chatbot.domain.repositories.chat_repository import ChatRepository


class AnswerQuestion:
    """
    Orchestrates the Retrieval-Augmented Generation (RAG) pipeline:

    1. Retrieve relevant documents via semantic similarity search.
    2. Build a context-aware prompt.
    3. Store the user message and the assistant reply in the chat history.
    """

    def __init__(
        self,
        chat_repository: ChatRepository,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        top_k: int = 5,
    ) -> None:
        self._chat_repo = chat_repository
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._top_k = top_k

    def execute(self, session_id: UUID, user_input: str) -> str:
        """
        Process *user_input* for *session_id* and return the assistant's reply.

        The reply is assembled from the most relevant document excerpts found
        in the vector store.  A concrete LLM integration can replace the
        context-assembly step in a subclass or via dependency injection.
        """
        user_message = Message(
            role=Role.USER, content=user_input, session_id=session_id
        )
        self._chat_repo.save_message(user_message)

        query_embedding = self._embedding_provider.embed(user_input)
        results = self._vector_store.search(query_embedding, top_k=self._top_k)

        context = self._build_context(results)
        reply = self._generate_reply(user_input, context)

        assistant_message = Message(
            role=Role.ASSISTANT, content=reply, session_id=session_id
        )
        self._chat_repo.save_message(assistant_message)
        return reply

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_context(results: list) -> str:
        """Concatenate retrieved document excerpts into a single context string."""
        if not results:
            return ""
        return "\n\n".join(doc.content for doc, _score in results)

    @staticmethod
    def _generate_reply(question: str, context: str) -> str:
        """
        Generate a reply from *question* and *context*.

        Override this method (or inject an LLM callable) to connect a real
        language model.  The default implementation returns the context so the
        architecture can be validated end-to-end without an LLM dependency.
        """
        if not context:
            return "I could not find relevant information to answer your question."
        return (
            f"Based on the available information:\n\n{context}\n\n"
            f"Question: {question}"
        )

    def get_history(self, session_id: UUID) -> List[Message]:
        """Return the full conversation history for *session_id*."""
        return self._chat_repo.get_history(session_id)
