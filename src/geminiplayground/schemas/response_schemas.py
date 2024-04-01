from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, Field, HttpUrl

from .parts_schemas import FilePart, FilePartData


# File schemas
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
        """
        Convert the fileInfo to a FilePart
        :return:
        """
        return FilePart(file_data=FilePartData(file_uri=str(self.uri), mime_type=self.mime_type))


# Model schemas
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


# Generation schema
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
