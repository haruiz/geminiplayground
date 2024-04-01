from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from .parts_schemas import FilePart, TextPart


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


class HarmCategory(str, Enum):
    SEXUALLY_EXPLICIT = "HARM_CATEGORY_SEXUALLY_EXPLICIT"
    HATE_SPEECH = "HARM_CATEGORY_HATE_SPEECH"
    HARASSMENT = "HARM_CATEGORY_HARASSMENT"
    DANGEROUS_CONTENT = "HARM_CATEGORY_DANGEROUS_CONTENT"


class HarmBlockThreshold(str, Enum):
    HARM_BLOCK_THRESHOLD_UNSPECIFIED = "HARM_BLOCK_THRESHOLD_UNSPECIFIED"
    BLOCK_LOW_AND_ABOVE = "BLOCK_LOW_AND_ABOVE"
    BLOCK_MEDIUM_AND_ABOVE = "BLOCK_MEDIUM_AND_ABOVE"
    BLOCK_ONLY_HIGH = "BLOCK_ONLY_HIGH"
    BLOCK_NONE = "BLOCK_NONE"


class SafetySettings(BaseModel):
    category: HarmCategory = Field(None, description="The category of harmful content to block.")
    threshold: HarmBlockThreshold = Field(None, description="The threshold of harmful content to block.")


class GenerateRequestParts(BaseModel):
    parts: list[TextPart | FilePart] = Field(..., description="Parts of the request.")


class GenerateRequest(BaseModel):
    contents: list[GenerateRequestParts] = Field(..., description="Contents of the request.")
    generation_config: GenerationSettings | dict = Field(None, alias="generationConfig",
                                                         description="Generation configuration.")
    safety_settings: dict = Field(None, alias="safetySettings", description="Safety settings.")
