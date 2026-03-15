"""Command-line interface for the chatbot."""
import sys
from uuid import uuid4

from chatbot.application.use_cases.answer_question import AnswerQuestion
from chatbot.application.use_cases.index_document import IndexDocument


class CLI:
    """Simple interactive REPL for the chatbot.

    Parameters
    ----------
    answer_question:
        Configured :class:`~chatbot.application.use_cases.answer_question.AnswerQuestion`
        use-case instance.
    index_document:
        Configured :class:`~chatbot.application.use_cases.index_document.IndexDocument`
        use-case instance.
    """

    QUIT_COMMANDS = {"quit", "exit", "q"}
    INDEX_PREFIX = "/index "

    def __init__(
        self,
        answer_question: AnswerQuestion,
        index_document: IndexDocument,
    ) -> None:
        self._answer = answer_question
        self._index = index_document
        self._session_id = uuid4()

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Start the interactive REPL loop."""
        print("Chatbot started. Type your question or use '/index <text>' to add")
        print("knowledge. Type 'quit' to exit.\n")
        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                sys.exit(0)

            if not user_input:
                continue
            if user_input.lower() in self.QUIT_COMMANDS:
                print("Goodbye!")
                sys.exit(0)
            if user_input.lower().startswith(self.INDEX_PREFIX):
                self._handle_index(user_input[len(self.INDEX_PREFIX):])
            else:
                self._handle_question(user_input)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _handle_question(self, text: str) -> None:
        reply = self._answer.execute(self._session_id, text)
        print(f"Assistant: {reply}\n")

    def _handle_index(self, text: str) -> None:
        from chatbot.domain.entities.document import Document  # noqa: PLC0415

        doc = Document(content=text, source="cli")
        self._index.execute(doc)
        print(f"[Indexed document {doc.doc_id}]\n")
