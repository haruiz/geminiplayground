import typing
from pathlib import Path
from typing import List

from google.generativeai.types import Tool

from .gemini_client import GeminiClient
from geminiplayground.utils import LibUtils
from pydantic import BaseModel


class ToolCall(BaseModel):
    """
    A message from the Gemini model.
    """

    tool_name: typing.Any
    tool_result: typing.Any


class Message(BaseModel):
    """
    A message from the Gemini model.
    """

    text: str


class ChatSession:
    """
    A chat session with the Gemini model.
    """

    @property
    def history(self):
        """
        Get the chat history.
        """
        return self.chat.history

    def __init__(self, model, toolbox, docs):
        self.model = model
        self.toolbox = toolbox
        self.docs = docs
        gemini_client = GeminiClient()
        tools_defs = [
            Tool(
                function_declarations=[
                    LibUtils.func_to_tool(tool_func)
                    for tool_name, tool_func in self.toolbox.items()
                ]
            )
        ]
        self.chat = gemini_client.start_chat(model=self.model, tools=tools_defs)

    def send_message(self, message: str, stream: bool = True) -> typing.Generator:
        """
        Send a message to the chat session.
        """
        response = self.chat.send_message(message, stream=stream)
        for response_chunk in response:
            for part in response_chunk.parts:
                if fn := part.function_call:
                    fun_name = fn.name
                    fun_args = dict(fn.args)
                    result = self.toolbox[fun_name](**fun_args)
                    yield ToolCall(tool_name=fun_name, tool_result=result)
                else:
                    yield Message(text=part.text)
        response.resolve()


class GeminiPlayground:
    """
    A playground for testing the Gemini model.
    """

    def __init__(
        self, model: str, metadata_index_config: dict, files_index_config: dict
    ):
        self.model = model
        self.playground_repository = None
        self.toolbox = {}
        self.history = []

        self.embeddings_model = None
        self.vector_index = None

    def add_file(self, file: typing.Union[str, Path]):
        """
        Add a file to the playground.
        @param file: The file to add
        """
        file = Path(file)
        if not file.exists():
            raise FileNotFoundError(f"File {file} not found")

        return self

    def add_tool(self, tool):
        """
        Add a tool to the playground.
        """
        self.tool(tool)

    def tool(self, func):
        """
        A decorator to add a tool to the playground.
        """
        # check for docstring
        if not func.__doc__:
            raise ValueError(f"Function {func.__name__} must have a docstring")
        # check for functions hints
        if not LibUtils.has_complete_type_hints(func):
            raise ValueError(f"Function {func.__name__} must have complete type hints")
        self.toolbox[func.__name__] = func

    def start_chat(self, docs: List[str] = None):
        """
        Start a chat session with the playground.
        """
        return ChatSession(self.model, self.toolbox, docs)
