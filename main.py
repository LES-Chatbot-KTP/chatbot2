"""Application entry point."""
from chatbot.application.use_cases.answer_question import AnswerQuestion
from chatbot.application.use_cases.index_document import IndexDocument
from chatbot.config.settings import Settings
from chatbot.infrastructure.embeddings.openai_embedding_provider import (
    OpenAIEmbeddingProvider,
)
from chatbot.infrastructure.repositories.in_memory_chat_repository import (
    InMemoryChatRepository,
)
from chatbot.infrastructure.repositories.in_memory_document_repository import (
    InMemoryDocumentRepository,
)
from chatbot.infrastructure.vector_store.faiss_vector_store import FaissVectorStore
from chatbot.presentation.cli import CLI


def create_app(settings: Settings) -> CLI:
    """Wire all layers together and return a ready-to-run :class:`CLI`."""
    embedding_provider = OpenAIEmbeddingProvider(settings)
    vector_store = FaissVectorStore()
    chat_repository = InMemoryChatRepository()
    document_repository = InMemoryDocumentRepository()

    answer_question = AnswerQuestion(
        chat_repository=chat_repository,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        top_k=settings.top_k,
    )
    index_document = IndexDocument(
        document_repository=document_repository,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )
    return CLI(answer_question=answer_question, index_document=index_document)


if __name__ == "__main__":
    app = create_app(Settings())
    app.run()
