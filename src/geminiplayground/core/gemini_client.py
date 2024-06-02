import logging
import os
import typing
from pathlib import Path
from time import sleep

import tenacity
from rich.console import Console
from rich.table import Table
from tqdm import tqdm
import google.generativeai as genai
from google.generativeai.types import Model, File

from geminiplayground.utils import Singleton

logger = logging.getLogger("rich")


def _normalize_prompt(prompt):
    """
    Normalize the prompt.
    :param prompt:
    :return:
    """
    from geminiplayground.parts import MultimodalPart

    normalized_prompt = []

    if isinstance(prompt, str):
        prompt = [prompt]

    for part in prompt:
        if isinstance(part, str):
            normalized_prompt.append(part)
        elif isinstance(part, MultimodalPart):
            content_parts = part.content_parts()
            normalized_prompt.extend(content_parts)
        elif isinstance(part, File):
            normalized_prompt.append(part)
        else:
            raise ValueError(f"Invalid prompt part: {part}")
    return normalized_prompt


class GeminiClient(metaclass=Singleton):
    """
    A client for the Gemini API.
    """

    def __init__(self, api_key=None):
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY", None)
        if not api_key:
            raise ValueError("GOOGLE_API_KEY must be provided.")
        self.api_key = api_key
        genai.configure(api_key=api_key)

    def print_models(self) -> None:
        """
        Print models in Gemini.
        :return:
        """
        models = self.query_models()
        table = Table(title="Models")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Display Name", style="magenta")
        table.add_column("Description")
        table.add_column("Input Token Limit")
        models = list(sorted(models, key=lambda m: m.input_token_limit, reverse=True))
        for model in models:
            table.add_row(
                model.name,
                model.description,
                model.display_name,
                str(model.output_token_limit),
            )

        console = Console()
        console.print(table)

    def print_files(self) -> None:
        """
        Print files in Gemini.
        :return:
        """
        files = self.query_files()
        table = Table(title="Files")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Expiration Time", style="magenta")
        table.add_column("Size (bytes)")
        table.add_column("MIME Type")
        table.add_column("URI")
        for file in files:
            table.add_row(
                file.name,
                file.expiration_time.strftime("%Y-%m-%d %H:%M:%S"),
                str(file.size_bytes),
                file.mime_type,
                file.uri,
            )

        console = Console()
        console.print(table)

    def query_models(self, **kwargs) -> typing.Iterable[Model]:
        """
        List models in Gemini.
        :return:
        """
        models = genai.list_models(**kwargs)
        return models

    def query_files(self, page_size: int = None) -> typing.Iterable[File]:
        """
        List files in Gemini.
        :param page_size: The number of files to return
        :return:
        """
        files = genai.list_files(page_size=page_size)
        return files

    def get_file(self, file_name: str) -> File:
        """
        Get information about a file in Gemini.
        :param file_name:
        :return:
        """
        file = genai.get_file(file_name)
        return file

    def delete_file(self, file_name: str) -> None:
        """
        Remove a file from Gemini.
        :param file_name:
        :return:
        """
        genai.delete_file(name=file_name)

    def upload_file(self, file_path: typing.Union[str, Path]) -> File:
        """
        Upload a file to Gemini.
        :param file_path: The path to the file
        :return:
        """
        # mime_type = mimetypes.guess_type(file_path)[0]
        file = genai.upload_file(path=file_path)
        return file

    def upload_files(self, *files: typing.List[str | Path], timeout: float = 0.0):
        """
        Upload multiple files to Gemini.
        :param timeout:  The time to wait between each file upload
        :param files: The files to upload
        :return:
        """
        uploaded_files = []
        for file in tqdm(files, desc="Uploading files"):
            sleep(timeout)
            uploaded_files.append(self.upload_file(file))
        return uploaded_files

    def delete_files(self, *files: typing.List[File | str], timeout: float = 0.5):
        """
        Remove multiple files from Gemini.
        :param timeout: The time to wait between each file deletion
        :param files: The files to remove
        :return:
        """

        files = [file.name if isinstance(file, File) else file for file in files]
        for file in tqdm(files, desc="Removing files"):
            sleep(timeout)
            self.delete_file(file)

    @tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(3))
    def count_tokens(self, model: str, prompt: typing.Any):
        """
        Get the number of tokens in a text.
        :param prompt:  The prompt
        :param model: The model to use
        :return:
        """
        model_names = [m.name for m in self.query_models()]
        assert (
            model in model_names
        ), f"Model {model} not found. Available models: {model_names}"

        model = genai.GenerativeModel(model)
        normalized_prompt = _normalize_prompt(prompt)
        response = model.count_tokens(normalized_prompt)
        return response

    def generate(
        self, model: str, prompt: typing.Any, system_instruction=None, **kwargs
    ):
        """
        Generate a response from a prompt.
        :param model: The model to use
        :param prompt: The prompt
        :return:
        """
        model_names = [m.name for m in self.query_models()]
        assert (
            model in model_names
        ), f"Model {model} not found. Available models: {model_names}"

        model = genai.GenerativeModel(model, system_instruction=system_instruction)
        response = model.generate_content(prompt, **kwargs)
        return response

    def stream(self, model: str, prompt: typing.Any, system_instruction=None, **kwargs):
        """
        Stream responses from a prompt.
        :param model: The model to use
        :param prompt: The prompt
        :param system_instruction: The system instruction
        :return:
        """
        model_names = [m.name for m in self.query_models()]
        assert (
            model in model_names
        ), f"Model {model} not found. Available models: {model_names}"

        model = genai.GenerativeModel(model, system_instruction=system_instruction)
        for message_chunk in model.generate_content(prompt, stream=True, **kwargs):
            yield message_chunk

    @tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(3))
    def generate_response(
        self,
        model: str,
        prompt: typing.Any,
        stream: bool = False,
        system_instruction=None,
        **kwargs,
    ):
        """
        Generate a response from a prompt.
        :param stream:  Whether to stream the response
        :param model: The model to use
        :param prompt: The prompt
        :param system_instruction: The system instruction
        :return:
        """
        normalized_prompt = _normalize_prompt(prompt)
        if stream:
            return self.stream(
                model,
                normalized_prompt,
                system_instruction=system_instruction,
                **kwargs,
            )
        return self.generate(
            model, normalized_prompt, system_instruction=system_instruction, **kwargs
        )

    def start_chat(self, model: str, history: list = None, tools: list = None):
        """
        Start a chat session.
        :param model: The model to use
        :param history: The chat history
        :param tools: The tools to use
        :return:
        """
        function_call_supported_models = [
            "models/gemini-1.0-pro",
            "models/gemini-1.0-pro-001",
            "models/gemini-1.5-pro-latest",
            "models/gemini-1.5-flash-latest",
        ]
        if len(tools) > 0 and model not in function_call_supported_models:
            raise ValueError(f"Model {model} does not support function calling. ")

        chat_model = genai.GenerativeModel(
            model_name="gemini-1.0-pro-001",
            generation_config=genai.GenerationConfig(temperature=0),
            tools=tools,
        )
        chat = chat_model.start_chat(history=history)
        return chat
