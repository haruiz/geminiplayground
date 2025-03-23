import logging
import os
from pathlib import Path
from time import sleep
from typing import Any, Iterable, List, Optional, Union

import tenacity
from google import genai
from google.genai.types import (
    Model,
    File,
    ListFilesConfig,
    GenerateContentConfigOrDict,
    CountTokensConfig,
)
from rich.console import Console
from rich.table import Table
from tqdm import tqdm

from geminiplayground.utils import Singleton, LibUtils

logger = logging.getLogger("rich")


class GeminiClient(metaclass=Singleton):
    """A client wrapper for the Gemini API using the new Google Generative AI SDK."""

    def __init__(self, api_key: Optional[str] = None, *args, **kwargs):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be provided.")
        self.api_client = genai.Client(api_key=self.api_key, *args, **kwargs)
        self.console = Console()

    def _assert_model_exists(self, model: str) -> None:
        model_names = [m.name for m in self.query_models()]
        if model not in model_names:
            raise ValueError(f"Model '{model}' not found. Available: {model_names}")

    def print_models(self) -> None:
        """Print available Gemini models."""
        models = sorted(self.query_models(), key=lambda m: m.input_token_limit, reverse=True)
        table = Table(title="Models")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Display Name", style="magenta")
        table.add_column("Description")
        table.add_column("Output Token Limit")

        for m in models:
            table.add_row(m.name, m.display_name, m.description, str(m.output_token_limit))

        self.console.print(table)

    def print_files(self) -> None:
        """Print uploaded Gemini files."""
        files = self.query_files()
        table = Table(title="Files")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Expiration Time", style="magenta")
        table.add_column("Size (bytes)")
        table.add_column("MIME Type")
        table.add_column("URI")

        for f in files:
            table.add_row(
                f.name,
                f.expiration_time.strftime("%Y-%m-%d %H:%M:%S"),
                str(f.size_bytes),
                f.mime_type,
                f.uri,
            )

        self.console.print(table)

    def query_models(self, **kwargs) -> Iterable[Model]:
        """List Gemini models."""
        return self.api_client.models.list(**kwargs)

    def query_files(self, page_size: Optional[int] = None) -> Iterable[File]:
        """List uploaded files."""
        config = ListFilesConfig(page_size=page_size)
        return self.api_client.files.list(config=config)

    def get_file(self, file_name: str) -> File:
        """Retrieve file metadata."""
        return self.api_client.files.get(name=file_name)

    def delete_file(self, file_name: str) -> None:
        """Delete a file from Gemini."""
        self.api_client.files.delete(name=file_name)

    def upload_file(self, file_path: Union[str, Path]) -> File:
        """Upload a single file."""
        return self.api_client.files.upload(file=file_path)

    def upload_files(self, *files: Union[str, Path], timeout: float = 0.0) -> List[File]:
        """Upload multiple files."""
        return [
            self.upload_file(file)
            for file in tqdm(files, desc="Uploading files")
            if not sleep(timeout)
        ]

    def delete_files(self, *files: Union[File, str], timeout: float = 0.5) -> None:
        """Delete multiple files."""
        names = [f.name if isinstance(f, File) else f for f in files]
        for name in tqdm(names, desc="Removing files"):
            sleep(timeout)
            self.delete_file(name)

    @tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(3))
    def count_tokens(
            self,
            model: str,
            prompt: Any,
            config: Optional[CountTokensConfig] = None,
    ):
        """Count tokens for a given prompt."""
        self._assert_model_exists(model)
        contents = LibUtils.normalize_prompt(prompt)
        return self.api_client.models.count_tokens(model=model, contents=contents, config=config)

    def generate(
            self,
            model: str,
            prompt: Any,
            config: Optional[GenerateContentConfigOrDict] = None,
    ):
        """Generate a response from a prompt."""
        return self.api_client.models.generate_content(model=model, contents=prompt, config=config)

    def stream(
            self,
            model: str,
            prompt: Any,
            config: Optional[GenerateContentConfigOrDict] = None,
    ):
        """Stream generated responses."""
        stream = self.api_client.models.generate_content_stream(model=model, contents=prompt, config=config)
        for chunk in stream:
            yield chunk

    @tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(3))
    def generate_response(
            self,
            model: str,
            prompt: Any,
            stream: bool = False,
            config: Optional[GenerateContentConfigOrDict] = None,
    ):
        """Generate a response with optional streaming."""
        self._assert_model_exists(model)
        contents = LibUtils.normalize_prompt(prompt)
        return self.stream(model, contents, config) if stream else self.generate(model, contents, config)

    def start_chat(
            self,
            model: str,
            history: Optional[list] = None,
            config: Optional[GenerateContentConfigOrDict] = None
    ):
        """Start a chat session."""
        return self.api_client.chats.create(model=model, history=history or [], config=config)
