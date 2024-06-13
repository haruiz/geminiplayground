import logging
import typing
from pathlib import Path

import weaviate
from dotenv import load_dotenv, find_dotenv
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.retrievers import BaseRetriever
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_weaviate.vectorstores import WeaviateVectorStore
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from google.generativeai import GenerativeModel
from rich.console import Console

from .summarization_loader import SummarizationLoader
from .scored_retriever import ScoredRetriever

logging.basicConfig(level=logging.INFO)

load_dotenv(find_dotenv())


class SimpleRAG:
    """
    A RAG model for summarization.
    """

    def __init__(
            self,
            chat_model: typing.Union[BaseChatModel, str],
            embeddings_model: typing.Union[Embeddings, str],
            summarization_model: typing.Union[GenerativeModel, str],
            **kwargs
    ):
        self._chat_model = ChatGoogleGenerativeAI(model=chat_model, temperature=0.0)
        self._embeddings_model = GoogleGenerativeAIEmbeddings(model=embeddings_model, task_type="retrieval_document")
        self._summarization_model = summarization_model
        self._batch_docs_size = kwargs.get("batch_docs_size", 50)
        self._top_k = kwargs.get("top_k", 5)
        self._collection_name = kwargs.get("collection_name", "rag")
        self._weaviate_client = kwargs.get("weaviate_client", weaviate.connect_to_embedded())
        self._docs = []
        self.weaviate_vectorstore = WeaviateVectorStore(
            client=self._weaviate_client,
            index_name=self._collection_name,
            embedding=self._embeddings_model,
            text_key="page_content"
        )

    def add_file(self, file_path: str):
        """
        Add a file to the vector index.
        """
        file = Path(file_path)
        if not file.exists():
            raise FileNotFoundError(f"File {file} not found")

        supported_extensions = {".pdf", ".mp3", ".wav", ".mp4", ".jpg", ".jpeg", ".png"}
        if file.suffix not in supported_extensions:
            raise ValueError(f"File type {file.suffix} not supported")

        self._docs.append(file)

    def index_docs(self):
        """
        Index documents in the vector store.
        """
        assert self._docs, "No documents to index"
        loader = SummarizationLoader(self._summarization_model, *self._docs)
        docs = loader.load()
        self.weaviate_vectorstore.add_documents(docs, batch_size=self._batch_docs_size)

    def clear_index(self):
        """
        Reset the vector index.
        """
        if self._weaviate_client.collections.get(self._collection_name):
            self._weaviate_client.collections.delete(self._collection_name)

    def get_retriever(self) -> BaseRetriever:
        """
        Get the retriever.
        """
        return ScoredRetriever(vectorstore=self.weaviate_vectorstore, k=self._top_k)

    def docs_count(self):
        """
        Get the number of documents in the vector index.
        """
        collection = self._weaviate_client.collections.get(self._collection_name)
        count = 0
        for _ in collection.iterator():
            count += 1
            if count > 100000:
                break
        return count

    def get_chain(self):
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

    def invoke(self, question: str, chat_history=None):
        """
        Invoke the RAG workflow.
        """
        qa_chain = self.get_chain()
        result = qa_chain.invoke({"input": question, "chat_history": chat_history})
        return result

    def chat(self, chat_history=None):
        """
        Main function to execute the RAG workflow.
        """

        console = Console()
        if chat_history is None:
            chat_history = []

        while True:
            question = input("Question: ")
            if question.lower() == "exit":
                break
            result = self.invoke(question, chat_history)
            chat_history.extend([HumanMessage(content=question), result["answer"]])
            console.print(f"Answer: {result['answer']}")
            docs = result["context"]
            for doc in docs[:3]:
                console.log(doc)
