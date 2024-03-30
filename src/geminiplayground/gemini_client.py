import logging
import os
import time
from datetime import datetime
from functools import wraps
from typing import List, Literal

import googleapiclient
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pydantic import BaseModel, HttpUrl
from pydantic import Field
from rich.console import Console
from rich.table import Table
from tqdm import tqdm

from geminiplayground.singleton import Singleton
from geminiplayground.utils import UploadFile

logger = logging.getLogger("rich")


class TextPart(BaseModel):
    text: str = Field(..., description="Text content.")


class FilePartData(BaseModel):
    file_uri: str = Field(description="URI of the file.", alias="fileUri")
    mime_type: str = Field(description="MIME type of the file.", alias="mimeType")

    class Config:
        populate_by_name = True


class FilePart(BaseModel):
    file_data: FilePartData = Field(alias="fileData", description="Information about the file.")

    class Config:
        populate_by_name = True


class GenerationSettings(BaseModel):
    stopSequences: List[str] = Field(
        None, alias="stopSequences",
        description="The set of character sequences (up to 5) that will stop output generation. "
    )
    candidateCount: int = Field(
        None, alias="candidateCount",
        description="Number of generated responses to return.This value must be between [1, 8], inclusive. If unset, "
                    "this will default to 1."
    )
    maxOutputTokens: int = Field(
        None, alias="maxOutputTokens",
        description="The maximum number of tokens to generate. The default value varies by model, see the "
                    "Model.output_token_limit attribute of the Model returned from the getModel function."
    )
    temperature: float = Field(
        None, description="Controls randomness in generation. Lower values make the model more deterministic. High "
                          "values make the model more creative."
    )
    topP: float = Field(
        None, alias="topP",
        description="The maximum cumulative probability of tokens to consider when sampling."
    )
    topK: int = Field(
        None, alias="topK",
        description="The maximum number of tokens to consider when sampling."
    )


class GenerateRequestParts(BaseModel):
    parts: list[TextPart | FilePart] = Field(..., description="Parts of the request.")


class GenerateRequest(BaseModel):
    contents: list[GenerateRequestParts] = Field(..., description="Contents of the request.")
    generation_config: GenerationSettings | dict = Field(None, alias="generationConfig",
                                                         description="Generation configuration.")
    safety_settings: dict = Field(None, alias="safetySettings", description="Safety settings.")


class FileInfo(BaseModel):
    name: str = Field(..., description="Unique identifier for the file.")
    display_name: str = Field(
        None, alias="displayName", description="Human-readable name for the file."
    )
    mime_type: str = Field(..., alias="mimeType", description="MIME type of the file.")
    size_bytes: str = Field(
        ..., alias="sizeBytes", description="Size of the file in bytes."
    )
    create_time: datetime = Field(
        ..., alias="createTime", description="Time the file was created."
    )
    update_time: datetime = Field(
        ..., alias="updateTime", description="Time the file was last updated."
    )
    expiration_time: datetime = Field(
        ..., alias="expirationTime", description="Time the file will expire."
    )
    sha256Hash: str = Field(
        ..., alias="sha256Hash", description="SHA-256 hash of the file."
    )
    uri: HttpUrl = Field(..., description="URI of the file.")

    def to_file_part(self):
        return FilePart(file_data=FilePartData(file_uri=str(self.uri), mime_type=self.mime_type))


class ModelInfo(BaseModel):
    name: str = Field(..., description="Unique identifier for the model.")
    version: str = Field(..., description="Version of the model.")
    display_name: str = Field(
        ..., alias="displayName", description="Human-readable name for the model."
    )
    description: str = Field(
        ..., description="Description of what the model does and how it should be used."
    )
    count_text_tokens: int = Field(
        None, alias="countTextTokens", description="Number of tokens in the model."
    )
    input_token_limit: int = Field(
        ...,
        alias="inputTokenLimit",
        description="Maximum number of input tokens the model can handle.",
    )
    output_token_limit: int = Field(
        ...,
        alias="outputTokenLimit",
        description="Maximum number of output tokens the model can generate.",
    )
    supported_generation_methods: List[str] = Field(
        ...,
        alias="supportedGenerationMethods",
        description="List of generation methods supported by the model.",
    )
    temperature: float = Field(
        None,
        description="Controls randomness in generation. Lower values make the model more deterministic.",
    )
    topP: float = Field(
        None,
        alias="topP",
        description="Nucleus sampling parameter controlling the size of the probability mass to keep.",
    )
    topK: int = Field(
        None,
        alias="topK",
        description="Controls diversity of generation. Limits the number of tokens considered for each step.",
    )


class Part(BaseModel):
    text: str = Field(..., description="Text content.")


class Content(BaseModel):
    parts: List[Part] = Field(..., description="Parts of the content.")
    role: str = Field(..., description="Role of the content.")


class SafetyRating(BaseModel):
    category: Literal[
        "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "HARM_CATEGORY_HATE_SPEECH",
        "HARM_CATEGORY_HARASSMENT",
        "HARM_CATEGORY_DANGEROUS_CONTENT",
    ] = Field(..., description="Category of the content.")
    probability: Literal["NEGLIGIBLE"] = Field(
        ..., description="Probability of the content falling into the category."
    )


class Candidate(BaseModel):
    content: Content = Field(..., description="Content generated by the model.")
    finish_reason: str = Field(
        ...,
        alias="finishReason",
        description="Reason the model stopped generating content.",
    )
    index: int = Field(..., description="Index of the candidate in the list.")
    safety_ratings: List[SafetyRating] = Field(
        ..., alias="safetyRatings", description="Safety ratings for the content."
    )


class CandidatesSchema(BaseModel):
    candidates: List[Candidate] = Field(
        ..., description="List of candidates generated by the model."
    )


class HarmCategory:
    SEXUALLY_EXPLICIT = "HARM_CATEGORY_SEXUALLY_EXPLICIT"
    HATE_SPEECH = "HARM_CATEGORY_HATE_SPEECH"
    HARASSMENT = "HARM_CATEGORY_HARASSMENT"
    DANGEROUS_CONTENT = "HARM_CATEGORY_DANGEROUS_CONTENT"


class HarmBlockThreshold:
    HARM_BLOCK_THRESHOLD_UNSPECIFIED = "HARM_BLOCK_THRESHOLD_UNSPECIFIED"
    BLOCK_LOW_AND_ABOVE = "BLOCK_LOW_AND_ABOVE"
    BLOCK_MEDIUM_AND_ABOVE = "BLOCK_MEDIUM_AND_ABOVE"
    BLOCK_ONLY_HIGH = "BLOCK_ONLY_HIGH"
    BLOCK_NONE = "BLOCK_NONE"


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
        models = self.list_models()
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
    def list_models(self):
        """
        List models in Gemini.
        :return:
        """
        response = self.genai_service.models().list().execute()
        models = [ModelInfo.parse_obj(model) for model in response["models"]]
        return models

    @handle_exceptions
    def get_files(self, all_files=False):
        """
        Get a list of files uploaded to Gemini.
        :return:
        """

        files = []
        response = self.genai_service.files().list().execute()
        if all_files is False:
            # print(json.dumps(response, indent=2))
            return [FileInfo.parse_obj(file) for file in response["files"]]
        while "nextPageToken" in response:
            next_page_token = response["nextPageToken"]
            if next_page_token is None:
                break
            files.extend([FileInfo.parse_obj(file) for file in response["files"]])
            next_page_response = (
                self.genai_service.files().list(pageToken=next_page_token).execute()
            )
            response = next_page_response
        return files

    @handle_exceptions
    def find_files_by_display_name_prefix(self, file_name_prefix: str):
        """
        Find video frames in a file.
        :param file_name_prefix: The prefix of the video file
        :return:
        """
        files = []
        response = self.genai_service.files().list().execute()
        while "nextPageToken" in response:
            next_page_token = response["nextPageToken"]
            if next_page_token is None:
                break
            page_files = [FileInfo.parse_obj(file) for file in response["files"]]
            for file in page_files:
                if file.display_name.startswith(file_name_prefix):
                    files.append(file)
            next_page_response = (
                self.genai_service.files().list(pageToken=next_page_token).execute()
            )
            response = next_page_response
        files = list(sorted(files, key=lambda x: x.display_name))
        return files

    def get_file_parts(self, display_name_prefix: str):
        """
        Get the parts of a file.
        :param display_name_prefix: The prefix of the display name
        :return:
        """
        files = self.find_files_by_display_name_prefix(display_name_prefix)
        parts = [f.to_file_part() for f in files]
        return parts

    @handle_exceptions
    def get_file_by_display_name(self, file_display_name: str):
        """
        Find a file by name.
        :param file_display_name: The name of the file
        """
        response = self.genai_service.files().list().execute()
        while "nextPageToken" in response:
            next_page_token = response["nextPageToken"]
            if next_page_token is None:
                break
            page_files = [FileInfo.parse_obj(file) for file in response["files"]]
            for file in page_files:
                if file.display_name == file_display_name:
                    return file
            next_page_response = (
                self.genai_service.files().list(pageToken=next_page_token).execute()
            )
            response = next_page_response
        raise FileNotFoundError(f"File with {file_display_name} not found.")

    @handle_exceptions
    def remove_all_files(self):
        """
        Remove all files from Gemini.
        :return:
        """
        files = self.get_files(all_files=True)
        for file in tqdm(files, desc="Removing files"):
            wait_time = 1
            time.sleep(wait_time)
            self.remove_file(file.name)

    @handle_exceptions
    def remove_file(self, file_name):
        """
        Remove a file from Gemini.
        :param file_name:
        :return:
        """
        self.genai_service.files().delete(name=file_name).execute()

    @handle_exceptions
    def upload_file(self, upload_file: UploadFile, body: dict = None):
        """
        Upload a file to Gemini.
        :param body: The body of the request
        :param upload_file: The file to upload
        :return:
        """
        if body is None:
            body = {"file": {"display_name": upload_file.display_name}}
        response = (
            self.genai_service.media()
            .upload(
                media_body=upload_file.file_path,
                media_mime_type=upload_file.mimetype,
                body=body,
            )
            .execute()
        )
        file = FileInfo.parse_obj(response["file"])
        return file

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
    def get_tokens_count(self, model: str, prompt_request: GenerateRequest):
        """
        Get the number of tokens in a text.
        :param model: The model to use
        :param prompt_request: The prompt
        :return:
        """
        response = (
            self.genai_service.models()
            .countTokens(
                model=model, body=prompt_request.dict(exclude_none=True, by_alias=True)
            )
            .execute()
        )
        return response["totalTokens"]

    @handle_exceptions
    def generate_response(self, model: str, prompt_request: GenerateRequest | list,
                          generation_config: GenerationSettings | dict = None,
                          safety_settings: dict = None):
        """
        Generate a response from a prompt.
        :param generation_config: The generation configuration
        :param model: The model to use
        :param prompt_request: The prompt
        :return:
        """
        from geminiplayground import VideoFile, ImageFile

        if isinstance(prompt_request, list):
            parts = []
            for part in prompt_request:
                if isinstance(part, str):
                    parts.append(TextPart(text=part))
                elif isinstance(part, (VideoFile, ImageFile)):
                    parts.extend(part.content_parts())
            prompt_request = GenerateRequest(contents=[GenerateRequestParts(parts=parts)])
            if generation_config:
                prompt_request.generation_config = generation_config
            if safety_settings:
                prompt_request.safety_settings = safety_settings

        response = (
            self.genai_service.models()
            .generateContent(
                model=model,
                body=prompt_request.dict(exclude_none=True, by_alias=True)
            )
            .execute()
        )
        response = CandidatesSchema.parse_obj(response)
        return response
