"""Use a single chain to route an input to one of multiple retrieval qa chains."""
from __future__ import annotations

import typing

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.tools import create_retriever_tool

from .rag import RAG, RAGResponse


class AgenticToolUseRAG(RAG):
    """
    A RAG implementation using a ROUTER (MultiRetrievalQAChain)
    """

    def __init__(
            self,
            chat_model: BaseChatModel,
            retrievers_info: typing.List[dict],
            custom_tools: list = None,
            chat_history: typing.List[HumanMessage] = None
    ):
        super().__init__(chat_model, retrievers_info, chat_history)
        self._custom_tools = custom_tools or []

    def _get_retriever_tools(self):
        """
        Get the retriever tools.
        """
        tools = []
        document_prompt = PromptTemplate.from_template("{page_content} \n {file_path}")
        for retriever_info in self._retrievers_info:
            retriever = retriever_info.get("retriever")
            name = retriever_info.get("name")
            description = retriever_info.get("description")
            retriever_tool = create_retriever_tool(
                retriever,
                name=name,
                description=description,
                document_prompt=document_prompt
            )
            tools.append(retriever_tool)
        return tools

    def get_runnable(self):
        """
        Get the chain.
        """
        tools = self._get_retriever_tools() + self._custom_tools

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful assistant"),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

        agent = create_tool_calling_agent(self._chat_model, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
        return agent_executor

    def invoke(self, question: str) -> typing.Any:
        """
        Invoke the RAG model.
        """
        agent_executor = self.get_runnable()
        print("Chat history:", self._chat_history)
        result = agent_executor.invoke({"input": question, "chat_history": self._chat_history})
        return RAGResponse(
            answer=result["output"],
            docs=[]
        )
