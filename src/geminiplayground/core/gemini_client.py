import json
import logging
import os
import typing
from functools import wraps
from time import sleep

import googleapiclient
import pydantic
import requests
from geminiplayground.schemas import ChatHistory
from geminiplayground.schemas import ChatMessage
from geminiplayground.schemas import TextPart
from geminiplayground.schemas.extra_schemas import UploadFile
from geminiplayground.schemas.request_schemas import GenerateRequest
from geminiplayground.schemas.request_schemas import GenerateRequestParts
from geminiplayground.schemas.response_schemas import CandidatesSchema
from geminiplayground.schemas.response_schemas import FileInfo
from geminiplayground.schemas.response_schemas import ModelInfo
from geminiplayground.utils import Singleton
from googleapiclient.errors import HttpError
from rich.console import Console
from rich.table import Table
from tqdm import tqdm

logger = logging.getLogger("rich")


def handle_exceptions(func):
    """
    Decorator to handle exceptions.
    :param func:
    :return:
    """

    @wraps(func)
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HttpError as e:
            if e.resp.status == 404 or e.resp.status == 403:
                logger.error("Resource not found, or access denied.")
            elif e.resp.status == 429:
                logger.error(
                    "Rate limit exceeded. Please wait a few minutes before trying again."
                )
            elif e.resp.status == 500:
                logger.error("Internal server error. Please try again later.")
            else:
                logger.error(f"Unexpected error: {e}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise e

    return decorator


class ChatSession:
    def __init__(self, client, model, history=None):
        self.client = client
        self.model = model
        self.history = history

    def generate_response(self, user_prompt, stream=False, **kwargs):
        """
        Generate a response from a user prompt.
        :param user_prompt: The user prompt
        :param stream: Whether to stream the response
        :param kwargs: Additional arguments
        """
        try:
            user_prompt = self.client.normalize_prompt(user_prompt)
            self.history.append(ChatMessage(role="user", parts=user_prompt))
            model_response = self.client.generate_response(
                self.model, ChatHistory(messages=self.history), stream=stream, **kwargs
            )
            if stream:
                message_parts = []
                for chunk_response in model_response:
                    yield chunk_response
                    message_parts.extend(chunk_response.candidates[0].content.parts)
                squeezed_response = "".join([part.text for part in message_parts])
                message_parts = [TextPart(text=squeezed_response)]
                self.history.append(ChatMessage(role="model", parts=message_parts))
            else:
                model_response = self.client.generate(
                    self.model, ChatHistory(messages=self.history)
                )
                message_parts = model_response.candidates[0].content.parts
                self.history.append(ChatMessage(role="model", parts=message_parts))
                return model_response
        except (pydantic.ValidationError, HttpError, Exception) as e:
            logger.error(f"Error sending message: {e}")
            raise e

    def close(self):
        self.history = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class GeminiClient(metaclass=Singleton):
    """
    A client for the Gemini API.
    """

    def __init__(self, api_key=None, version="v1beta"):
        if not api_key:
            api_key = os.getenv("AISTUDIO_API_KEY", None)
        if not api_key:
            raise ValueError("AISTUDIO_API_KEY must be provided.")
        discovery_url = f"https://generativelanguage.googleapis.com/$discovery/rest?version={version}&key={api_key}"
        discovery_docs = requests.get(discovery_url).content
        self.genai_service = googleapiclient.discovery.build_from_document(
            discovery_docs, developerKey=api_key
        )

    def print_models(self):
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
        models = list(sorted(models, key=lambda x: x.inputTokenLimit, reverse=True))
        for model in models:
            table.add_row(
                model.name,
                model.description,
                model.displayName,
                str(model.inputTokenLimit),
            )

        console = Console()
        console.print(table)

    @handle_exceptions
    def query_models(self):
        """
        List models in Gemini.
        :return:
        """
        response = self.genai_service.models().list().execute()
        models = [ModelInfo.parse_obj(model) for model in response["models"]]
        return models

    @handle_exceptions
    def query_files(
        self, query_fn: typing.Callable | None = None, limit: int | None = None
    ):
        """
        List files in Gemini.
        :return:
        """
        files = []
        page_token = None
        while True:
            # Add conditional parameters only if they are needed
            request_params: dict = {}
            if page_token is not None:
                request_params["pageToken"] = page_token
            response = self.genai_service.files().list(**request_params).execute()
            files.extend(
                [FileInfo.parse_obj(file) for file in response.get("files", [])]
            )
            # Break the loop if not fetching all files or if there's no next page
            files = sorted(files, key=lambda x: x.create_time, reverse=True)
            if query_fn is not None:
                files = list(filter(query_fn, files))
            if limit is not None and len(files) >= limit:
                return files[:limit]
            page_token = response.get("nextPageToken")
            if page_token is None:
                break
        return files

    @handle_exceptions
    def get_file(self, file_name):
        """
        Get information about a file in Gemini.
        :param file_name:
        :return:
        """
        response = self.genai_service.files().get(name=file_name).execute()
        response = FileInfo.parse_obj(response)
        return response

    @handle_exceptions
    def delete_file(self, file_name: str):
        """
        Remove a file from Gemini.
        :param file_name:
        :return:
        """
        self.genai_service.files().delete(name=file_name).execute()

    @handle_exceptions
    def upload_file(self, upload_file: UploadFile):
        """
        Upload a file to Gemini.
        :param body: The body of the request
        :param upload_file: The file to upload
        :return:
        """
        response = (
            self.genai_service.media()
            .upload(
                media_body=upload_file.file_path,
                media_mime_type=upload_file.mimetype,
                body=upload_file.body,
            )
            .execute()
        )
        file = FileInfo.parse_obj(response["file"])
        return file

    @handle_exceptions
    def upload_files(self, *files: typing.List[UploadFile], timeout: float = 0.0):
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

    @handle_exceptions
    def delete_files(self, *files: typing.List[FileInfo | str], timeout: float = 0.5):
        """
        Remove multiple files from Gemini.
        :param timeout: The time to wait between each file deletion
        :param files: The files to remove
        :return:
        """

        files = [file.name if isinstance(file, FileInfo) else file for file in files]  # type: ignore
        for file in tqdm(files, desc="Removing files"):
            sleep(timeout)
            self.delete_file(file)

    @staticmethod
    # Adjust the type hint for `prompt_request` to indicate it can be one of several types
    def normalize_prompt(prompt: list | str) -> typing.List:
        """
        Get the parts of a prompt, and convert it to a GenerateRequest object.
        :param prompt: The prompt
        :return: A GenerateRequest object.
        """
        from geminiplayground.schemas import TextPart, FilePart
        from geminiplayground.parts import MultimodalPart

        parts = []
        # Normalize input to always be a list
        if isinstance(prompt, str):
            prompt = [prompt]

        for part in prompt:
            if isinstance(part, str):
                parts.append(TextPart(text="\n" + part + "\n"))
            elif isinstance(part, MultimodalPart):
                parts.extend(part.content_parts())
            elif isinstance(part, (TextPart, FilePart)):
                parts.append(part)
        return parts

    @handle_exceptions
    def get_tokens_count(self, model: str, prompt: GenerateRequest | list):
        """
        Get the number of tokens in a text.
        :param prompt:  The prompt
        :param model: The model to use
        :return:
        """
        if isinstance(prompt, GenerateRequest):
            generate_request = prompt
        else:
            prompt = self.normalize_prompt(prompt)
            generate_request = GenerateRequest(
                contents=[GenerateRequestParts(parts=prompt)]
            )
        response = (
            self.genai_service.models()
            .countTokens(
                model=model,
                body=generate_request.dict(exclude_none=True, by_alias=True),
            )
            .execute()
        )
        return response["totalTokens"]

    @handle_exceptions
    def generate(
        self,
        model: str,
        prompt: GenerateRequest | ChatHistory | list | str | dict,
        **kwargs,
    ) -> CandidatesSchema:
        """
        Generate a response from a prompt.
        :param model: The model to use
        :param prompt: The prompt
        :return:
        """
        generate_request = self.__mk_generative_request(prompt, **kwargs)

        try:
            response = (
                self.genai_service.models()
                .generateContent(
                    model=model,
                    body=generate_request.dict(exclude_none=True, by_alias=True),
                )
                .execute()
            )
            logger.debug(json.dumps(response, indent=2))
            response = CandidatesSchema.parse_obj(response)
            return response
        except pydantic.ValidationError as e:
            logger.error(f"Error parsing response: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise e

    @handle_exceptions
    def stream(self, model: str, prompt: GenerateRequest | list | str | dict, **kwargs):
        """
        Stream responses from a prompt.
        :param timeout: The timeout to wait for the next candidate
        :param model: The model to use
        :param prompt: The prompt
        :param kwargs: Additional arguments
        :return:
        """
        generate_request = self.__mk_generative_request(prompt, **kwargs)
        timeout = kwargs.get("timeout", 0.0)
        response = (
            self.genai_service.models()
            .streamGenerateContent(
                model=model,
                body=generate_request.dict(exclude_none=True, by_alias=True),
                alt="json",
            )
            .execute()
        )
        for chunk in response:
            if timeout:
                sleep(timeout)
            chunk_response = CandidatesSchema.parse_obj(chunk)
            yield chunk_response

    def __mk_generative_request(self, prompt, **kwargs):
        assert isinstance(
            prompt, (GenerateRequest, ChatHistory, list, str)
        ), "Prompt must be a GenerateRequest, ChatHistory, list, or str"
        if isinstance(prompt, GenerateRequest):
            generate_request = prompt
        elif isinstance(prompt, ChatHistory):
            generate_request = GenerateRequest(contents=prompt.messages)
        else:
            prompt = self.normalize_prompt(prompt)
            generate_request = GenerateRequest(
                contents=[GenerateRequestParts(parts=prompt)]
            )
        generation_config = kwargs.get("generation_config", None)
        safety_settings = kwargs.get("safety_settings", None)
        if generation_config is not None:
            generate_request.generation_config = generation_config
        if safety_settings is not None:
            generate_request.safety_settings = safety_settings
        return generate_request

    def generate_response(
        self,
        model: str,
        prompt: GenerateRequest | list | str | dict,
        stream: bool = False,
        **kwargs,
    ):
        """
        Generate a response from a prompt.
        :param stream:  Whether to stream the response
        :param model: The model to use
        :param prompt: The prompt
        :return:
        """
        if stream:
            return self.stream(model, prompt, **kwargs)
        return self.generate(model, prompt, **kwargs)

    @handle_exceptions
    def start_chat(self, model: str, history: list | ChatHistory = None, **kwargs):
        """
        Start a chat session.
        :param model: The model to use
        :param history: The chat history
        :return:
        """
        if isinstance(history, ChatHistory):
            history = history.messages
        return ChatSession(self, model, history, **kwargs)
