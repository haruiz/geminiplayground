"""Use a single chain to route an input to one of multiple retrieval qa chains."""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate
from langchain_core.retrievers import BaseRetriever

from langchain.chains import ConversationChain
from langchain.chains.base import Chain
from langchain.chains.conversation.prompt import DEFAULT_TEMPLATE
from langchain.chains.retrieval_qa.base import BaseRetrievalQA, RetrievalQA
from langchain.chains.router.base import MultiRouteChain
from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser
from langchain.chains.router.multi_retrieval_prompt import (
    MULTI_RETRIEVAL_ROUTER_TEMPLATE,
)

from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage
from rich.console import Console

from geminiplayground.rag.scored_retriever import ScoredRetriever
from geminiplayground.rag.summarization_loader import SummarizationLoader

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
import logging


class MultiRetrievalQAChain(MultiRouteChain):
    """A multi-route chain that uses an LLM router chain to choose amongst retrieval
    qa chains."""

    router_chain: LLMRouterChain
    """Chain for deciding a destination chain and the input to it."""
    destination_chains: Mapping[str, BaseRetrievalQA]
    """Map of name to candidate chains that inputs can be routed to."""
    default_chain: Chain
    """Default chain to use when router doesn't map input to one of the destinations."""

    @property
    def output_keys(self) -> List[str]:
        return ["result"]

    @classmethod
    def from_retrievers(
            cls,
            llm: BaseLanguageModel,
            retriever_infos: List[Dict[str, Any]],
            default_retriever: Optional[BaseRetriever] = None,
            default_prompt: Optional[PromptTemplate] = None,
            default_chain: Optional[Chain] = None,
            *,
            default_chain_llm: Optional[BaseLanguageModel] = None,
            **kwargs: Any,
    ) -> MultiRetrievalQAChain:
        if default_prompt and not default_retriever:
            raise ValueError(
                "`default_retriever` must be specified if `default_prompt` is "
                "provided. Received only `default_prompt`."
            )
        destinations = [f"{r['name']}: {r['description']}" for r in retriever_infos]
        destinations_str = "\n".join(destinations)
        router_template = MULTI_RETRIEVAL_ROUTER_TEMPLATE.format(
            destinations=destinations_str
        )
        router_prompt = PromptTemplate(
            template=router_template,
            input_variables=["input"],
            output_parser=RouterOutputParser(next_inputs_inner_key="query"),
        )
        router_chain = LLMRouterChain.from_llm(llm, router_prompt)
        destination_chains = {}
        for r_info in retriever_infos:
            prompt = r_info.get("prompt")
            retriever = r_info["retriever"]
            chain = RetrievalQA.from_llm(
                llm, prompt=prompt, retriever=retriever, return_source_documents=True
            )

            name = r_info["name"]
            destination_chains[name] = chain
        if default_chain:
            _default_chain = default_chain
        elif default_retriever:
            _default_chain = RetrievalQA.from_llm(
                llm, prompt=default_prompt, retriever=default_retriever, return_source_documents=True
            )
        else:
            prompt_template = DEFAULT_TEMPLATE.replace("input", "query")
            prompt = PromptTemplate(
                template=prompt_template, input_variables=["history", "query"]
            )
            if default_chain_llm is None:
                raise NotImplementedError(
                    "conversation_llm must be provided if default_chain is not "
                    "specified. This API has been changed to avoid instantiating "
                    "default LLMs on behalf of users."
                    "You can provide a conversation LLM like so:\n"
                    "from langchain_openai import ChatOpenAI\n"
                    "llm = ChatOpenAI()"
                )
            _default_chain = ConversationChain(
                llm=default_chain_llm,
                prompt=prompt,
                input_key="query",
                output_key="result",
            )
        return cls(
            router_chain=router_chain,
            destination_chains=destination_chains,
            default_chain=_default_chain,
            **kwargs,
        )


class AgenticRAG:
    """
    A RAG model for summarization.
    """

    def __init__(self, summarization_model: str, chat_model: str, embeddings_model: str):
        self._chat_model = ChatGoogleGenerativeAI(model=chat_model, temperature=0.0)
        self._embeddings_model = GoogleGenerativeAIEmbeddings(model=embeddings_model, task_type="retrieval_document")
        self._summarization_model = summarization_model
        self._batch_docs_size = 50
        self._files = []

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

        self._files.append(file)

    def get_retrievers_info(self):
        """
        get retrievers info
        """
        retrievers_info = []

        for file in self._files:
            loader = SummarizationLoader(self._summarization_model, file)
            docs = loader.load()
            doc_batches = [docs[i:i + self._batch_docs_size] for i in range(0, len(docs), self._batch_docs_size)]
            vector_store = FAISS.from_documents(doc_batches[0], self._embeddings_model)
            for batch in doc_batches[1:]:
                logging.info(f"Adding batch of {len(batch)} documents to vector store")
                vector_store.add_documents(batch)
            retrievers_info.append({
                "name": str(file),
                "description": f"Retriever for file {file}",
                "retriever": ScoredRetriever(vectorstore=vector_store, k=5),
            })
        return retrievers_info

    def chat(self, chat_history=None):
        """
        Chat with the model.
        """
        DEFAULT_TEMPLATE = """The following is a friendly conversation between a human and an AI. The AI is talkative 
        and provides lots of specific details from its context. If the AI does not know the answer to a question, 
        it truthfully says it does not know.

        Current conversation:
        {history}
        Human: {input}
        AI:"""
        if chat_history is None:
            chat_history = []

        prompt_default_template = DEFAULT_TEMPLATE.replace('input', 'query')

        prompt_default = PromptTemplate(
            template=prompt_default_template, input_variables=['history', 'query']
        )
        default_chain = ConversationChain(llm=self._chat_model, prompt=prompt_default, input_key='query',
                                          output_key='result')
        retrievers = self.get_retrievers_info()
        qa_chain = MultiRetrievalQAChain.from_retrievers(llm=self._chat_model, retriever_infos=retrievers,
                                                         default_chain=default_chain,
                                                         verbose=True)
        console = Console()
        while True:
            user_input = input("You: ")
            if user_input == "exit":
                break
            result = qa_chain.invoke({"input": user_input, "chat_history": chat_history})
            chat_history.extend([HumanMessage(content=user_input), result["result"]])
            console.print(f"Answer: {result['result']}")
            if "source_documents" in result:
                print("Source documents:")
                for doc in result["source_documents"]:
                    console.print(doc)
