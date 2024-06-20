import typing
from abc import abstractmethod, ABC

from langchain_core.messages import HumanMessage
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import Runnable
from pydantic import BaseModel
from rich.console import Console
from langchain_core.language_models import BaseChatModel


class RAGResponse(BaseModel):
    answer: str
    docs: list


class RAG(ABC):
    """
    A RAG model for summarization.
    """

    def __init__(
            self,
            chat_model: BaseChatModel,
            retrievers_info: typing.List[typing.Union[BaseRetriever, typing.Dict[str, typing.Any]]],
            chat_history: typing.List[HumanMessage] = None
    ):
        self._chat_model = chat_model
        self._retrievers_info = retrievers_info
        self._chat_history = chat_history or []

    @property
    def chat_history(self):
        """
        Get the chat history.
        """
        return self._chat_history

    @abstractmethod
    def get_runnable(self) -> Runnable:
        """
        Get the RAG runnable
        """
        raise NotImplementedError("This function must be implemented in the subclass.")

    @abstractmethod
    def invoke(self, question: str) -> RAGResponse:
        """
        Invoke the RAG model.
        """
        raise NotImplementedError("This function must be implemented in the subclass.")

    def chat(self):
        """
        Main function to execute the RAG workflow.
        """

        console = Console()
        while True:
            question = input("Question: ")
            if question.lower() == "exit":
                break
            result = self.invoke(question)
            self._chat_history.extend([HumanMessage(content=question), result.answer])
            console.print(f"Answer: {result.answer}")
            docs = result.docs
            for doc in docs[:3]:
                console.print(doc)
