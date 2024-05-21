import typing
from typing import List

from pydantic import BaseModel
from pydantic import Field

from .enums import HarmBlockThreshold
from .enums import HarmCategory
from .parts_schemas import FilePart
from .parts_schemas import TextPart


class GenerationSettings(BaseModel):
    stop_sequences: typing.Optional[List[str]] = Field(
        None,
        alias="stopSequences",
        description="The set of character sequences (up to 5) that will stop output generation. ",
    )
    candidate_count: typing.Optional[int] = Field(
        None,
        alias="candidateCount",
        description="Number of generated responses to return.This value must be between [1, 8], inclusive. If unset, "
        "this will default to 1.",
    )
    max_output_tokens: typing.Optional[int] = Field(
        None,
        alias="maxOutputTokens",
        description="The maximum number of tokens to generate. The default value varies by model, see the "
        "Model.output_token_limit attribute of the Model returned from the getModel function.",
    )
    temperature: typing.Optional[float] = Field(
        None,
        description="Controls randomness in generation. Lower values make the model more deterministic. High "
        "values make the model more creative.",
    )
    top_p: typing.Optional[float] = Field(
        None,
        alias="topP",
        description="The maximum cumulative probability of tokens to consider when sampling.",
    )
    top_k: typing.Optional[int] = Field(
        None,
        alias="topK",
        description="The maximum number of tokens to consider when sampling.",
    )

    class Config:
        populate_by_name = True


class SafetySettings(BaseModel):
    category: HarmCategory = Field(
        None, description="The category of harmful content to block."
    )
    threshold: HarmBlockThreshold = Field(
        None, description="The threshold of harmful content to block."
    )

    class Config:
        populate_by_name = True


class ChatMessage(BaseModel):
    role: typing.Literal["model", "user"] = Field(..., description="Role of the part.")
    parts: list[TextPart | FilePart] = Field(..., description="Parts of the content.")

    class Config:
        populate_by_name = True


class ChatHistory(BaseModel):
    messages: list[ChatMessage] = Field(..., description="Chat message history.")

    class Config:
        populate_by_name = True


class GenerateRequestParts(BaseModel):
    parts: list[TextPart | FilePart] = Field(..., description="Parts of the request.")

    class Config:
        populate_by_name = True


class GenerateRequest(BaseModel):
    contents: list[GenerateRequestParts | ChatMessage] | dict = Field(
        ..., description="Contents of the request."
    )
    generation_config: typing.Optional[GenerationSettings | dict] = Field(
        None, alias="generationConfig", description="Generation configuration."
    )
    safety_settings: typing.Optional[dict] = Field(
        None, alias="safetySettings", description="Safety settings."
    )

    class Config:
        populate_by_name = True
