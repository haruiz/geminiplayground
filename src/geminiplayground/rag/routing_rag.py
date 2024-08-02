"""Use a single chain to route an input to one of multiple retrieval qa chains."""
from __future__ import annotations

import typing
from typing import Any, Dict, List, Mapping, Optional

from langchain_core.language_models import BaseLanguageModel, BaseChatModel
from langchain_core.messages import HumanMessage
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

from .rag import RAG, RAGResponse


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


class RoutingRAG(RAG):
    """
    A RAG implementation using a ROUTER (MultiRetrievalQAChain)
    """

    def __init__(
            self,
            chat_model: BaseChatModel,
            retrievers_info: typing.List[dict],
            chat_history: typing.List[HumanMessage] = None
    ):
        super().__init__(chat_model, retrievers_info, chat_history)

    def invoke(self, question: str) -> RAGResponse:
        """
        Invoke the RAG model.
        """
        qa_chain = self.get_runnable()
        result = qa_chain.invoke({"input": question, "chat_history": self._chat_history})

        docs = result.get("source_documents", [])
        answer = result.get("result", None)

        return RAGResponse(
            answer=answer,
            docs=docs
        )

    def get_runnable(self):
        """
        Get the chain.
        """

        DEFAULT_TEMPLATE = """The following is a friendly conversation between a human and an AI. The AI is talkative 
                and provides lots of specific details from its context. If the AI does not know the answer to a question, 
                it truthfully says it does not know.
                Current conversation:
                {history}
                Human: {input}
                AI:"""
        default_prompt_template = DEFAULT_TEMPLATE.replace('input', 'query')
        default_prompt = PromptTemplate(
            template=default_prompt_template, input_variables=['history', 'query']
        )
        default_chain = ConversationChain(llm=self._chat_model, prompt=default_prompt, input_key='query',
                                          output_key='result')
        return MultiRetrievalQAChain.from_retrievers(llm=self._chat_model, retriever_infos=self._retrievers_info,
                                                     default_chain=default_chain,
                                                     verbose=True)
