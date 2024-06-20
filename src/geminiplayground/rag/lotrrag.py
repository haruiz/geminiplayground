import logging
import typing

from dotenv import load_dotenv, find_dotenv
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.retrievers import MergerRetriever
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import Runnable
from langchain_core.language_models import BaseChatModel
from .rag import RAG, RAGResponse

logging.basicConfig(level=logging.INFO)

load_dotenv(find_dotenv())


class LOTRRAG(RAG):
    """
    A RAG implementation using LOTR (Merger Retriever)
    """

    def __init__(
            self,
            chat_model: BaseChatModel,
            retrievers_info: typing.List[dict],
            chat_history: typing.List[HumanMessage] = None
    ):
        super().__init__(chat_model, retrievers_info, chat_history)

    def get_retriever(self) -> BaseRetriever:
        """
        Get the retriever.
        """
        assert len(self._retrievers_info) > 0, "At least one retriever is required."

        # Single retriever
        if len(self._retrievers_info) == 1:
            return self._retrievers_info[0].get("retriever")

        # LOTR (Merger Retriever)
        lotr_retriever = MergerRetriever(retrievers=[
            retriever["retriever"] for retriever in self._retrievers_info
        ])
        return lotr_retriever

    def invoke(self, question: str) -> RAGResponse:
        """
        Invoke the RAG model.
        """
        qa_chain = self.get_runnable()
        result = qa_chain.invoke({"input": question, "chat_history": self._chat_history})
        return RAGResponse(
            answer=result["answer"],
            docs=result["context"]
        )

    def get_runnable(self) -> Runnable:
        """
        Get the RAG chain.
        """
        retriever = self.get_retriever()
        llm = self._chat_model
        contextualize_q_system_prompt = """Given a chat history and the latest user question \
               which might reference context in the chat history, formulate a standalone question \
               which can be understood without the chat history. Do NOT answer the question, \
               just reformulate it if needed and otherwise return it as is."""
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        history_aware_retriever = create_history_aware_retriever(
            llm, retriever, contextualize_q_prompt
        )

        qa_system_prompt = """You are an assistant for question-answering tasks. \
               Use the following pieces of retrieved context to answer the question. \
               If you don't know the answer, just say that you don't know. \
               Use three sentences maximum and keep the answer concise.\

               {context}"""
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
        rag_chain_with_chat_history = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        return rag_chain_with_chat_history
