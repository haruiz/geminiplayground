import logging
import typing
from pathlib import Path

from google.genai.chats import Chat
from google.genai.types import Tool, GenerateContentConfig
from pydantic import BaseModel

from geminiplayground.utils import LibUtils
from .gemini_client import GeminiClient

logger = logging.getLogger("rich")


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

    def __init__(self, model: str, history: list, toolbox: dict, *args, **kwargs):
        self.model = model
        self.toolbox = toolbox
        self.history = history
        self.gemini_client = kwargs.pop("gemini_client", GeminiClient(*args, **kwargs))
        self.chat: Chat = self._create_chat()

    def _create_chat(self) -> Chat:
        """
        Creates and initializes the Gemini Chat instance.
        """
        tool_configs = list(self.toolbox.values())
        return self.gemini_client.start_chat(
            model=self.model,
            history=self.history,
            config=GenerateContentConfig(tools=tool_configs),
        )

    def reset_chat(self) -> None:
        """
        Resets the chat session, clearing history and tools.
        """
        self.chat = self._create_chat()

    def send_message(self, message: str, config: GenerateContentConfig = None) -> typing.Generator:
        """
        Send a message to the chat session.
        """
        normalized_message = LibUtils.normalize_prompt(message)
        response = self.chat.send_message_stream(normalized_message, config=config)
        for chunk in response:
            yield Message(text=chunk.text)


class GeminiPlayground:
    """
    A playground for testing the Gemini model.
    """

    def __init__(
            self, model: str
    ):
        self.model = model
        self.toolbox = {}

    def add_file(self, file: typing.Union[str, Path]):
        """
        Add a file to the playground.
        @param file: The file to add
        """
        raise NotImplementedError("Not implemented yet")

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

    def start_chat(self, history: list = None, **kwargs):
        """
        Start a chat session with the playground.
        """
        return ChatSession(self.model, history, self.toolbox, **kwargs)
