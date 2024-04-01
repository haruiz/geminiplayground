import json
import logging
import os
import typing
from functools import wraps
from time import sleep

import googleapiclient
import pydantic
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from rich.console import Console
from rich.table import Table
from tqdm import tqdm

from geminiplayground.schemas.extra_schemas import UploadFile
from geminiplayground.schemas.request_schemas import (
    GenerationSettings,
    GenerateRequestParts,
    GenerateRequest,
)
from geminiplayground.schemas.response_schemas import (
    FileInfo,
    ModelInfo,
    CandidatesSchema,
)
from geminiplayground.utils import Singleton

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
                logger.error(f"Resource not found, or access denied.")
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


class GeminiClient(metaclass=Singleton):
    """
    A client for the Gemini API.
    """

    def __init__(self, api_key=None):
        if not api_key:
            api_key = os.getenv("AISTUDIO_API_KEY", None)
        if not api_key:
            raise ValueError("API_KEY must be provided.")
        discovery_url = f"https://generativelanguage.googleapis.com/$discovery/rest?version=v1beta&key={api_key}"
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
    def query_files(self, query_fn: typing.Callable = None, limit: int = None):
        """
        List files in Gemini.
        :return:
        """
        files = []
        page_token = None
        while True:
            # Add conditional parameters only if they are needed
            request_params = {}
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
        # with ThreadPoolExecutor(max_workers=max_workers) as executor:
        #     tasks = [executor.submit(self.upload_file, file) for file in files]
        #     with tqdm(total=len(tasks), desc="Uploading files") as progress:
        #         for future in as_completed(tasks):
        #             result = future.result()  # You can use the result here if needed
        #             uploaded_files.append(result)
        #             progress.update(1)  # Update the progress bar by one
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
        if all(isinstance(file, FileInfo) for file in files):
            files = [file.name for file in files]

        # with ThreadPoolExecutor(max_workers=max_workers) as executor:
        #     tasks = [executor.submit(self.delete_file, file) for file in files]
        #     with tqdm(total=len(tasks), desc="Removing files") as progress:
        #         for future in as_completed(tasks):
        #             future.result()
        #             progress.update(1)
        for file in tqdm(files, desc="Removing files"):
            sleep(timeout)
            self.delete_file(file)

    @staticmethod
    def normalize_prompt_request(prompt_request: GenerateRequest | list):
        """
        Get the parts of a prompt, and convert it to a GenerateRequest object.
        :param prompt_request:
        :return:
        """
        from geminiplayground.schemas import TextPart
        from geminiplayground.parts import MultimodalPart

        if isinstance(prompt_request, list):
            parts = []
            for part in prompt_request:
                if isinstance(part, str):
                    parts.append(TextPart(text="\n" + part + "\n"))
                elif isinstance(part, MultimodalPart):
                    parts.extend(part.content_parts())
            prompt_request = GenerateRequest(
                contents=[GenerateRequestParts(parts=parts)]
            )
        return prompt_request

    @handle_exceptions
    def get_tokens_count(self, model: str, prompt_request: GenerateRequest | list):
        """
        Get the number of tokens in a text.
        :param model: The model to use
        :param prompt_request: The prompt
        :return:
        """
        prompt_request = self.normalize_prompt_request(prompt_request)

        response = (
            self.genai_service.models()
            .countTokens(
                model=model, body=prompt_request.dict(exclude_none=True, by_alias=True)
            )
            .execute()
        )
        return response["totalTokens"]

    @handle_exceptions
    def generate_response(
        self,
        model: str,
        prompt_request: GenerateRequest | list,
        generation_config: GenerationSettings | dict = None,
        safety_settings: dict = None,
    ):
        """
        Generate a response from a prompt.
        :param model: The model to use
        :param prompt_request: The prompt
        :param generation_config: Generation settings
        :param safety_settings: Safety settings
        :return:
        """

        prompt_request = self.normalize_prompt_request(prompt_request)
        if generation_config:
            prompt_request.generation_config = generation_config
        if safety_settings:
            prompt_request.safety_settings = safety_settings

        response = (
            self.genai_service.models()
            .generateContent(
                model=model, body=prompt_request.dict(exclude_none=True, by_alias=True)
            )
            .execute()
        )
        try:
            response = CandidatesSchema.parse_obj(response)
            return response
        except pydantic.ValidationError as e:
            logger.error(f"Error parsing response: {e}")
            logger.error(json.dumps(response, indent=2))
            raise e
