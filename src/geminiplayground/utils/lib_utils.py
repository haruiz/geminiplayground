import inspect
import os
import re
import typing
from datetime import datetime, timezone
from pathlib import Path

from PIL.Image import Image
from google.genai.types import File, FunctionDeclaration
from langchain_core.documents import Document
from pydantic import BaseModel, Field, create_model


class LibUtils:
    """
    A collection of utility methods for use in the Gemini playground environment.
    """

    @staticmethod
    def get_lib_home() -> Path:
        """
        Retrieve the cache directory for Gemini Playground.

        Returns:
            Path object to the cache directory.
        """
        cache_dir = os.environ.get("GEMINI_PLAYGROUND_HOME", Path.home() / ".gemini_playground")
        cache_dir = Path(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    @staticmethod
    def get_uploaded_file_exp_date_delta_t(uploaded_file: File) -> float:
        """
        Calculate time remaining until expiration of an uploaded file.

        Args:
            uploaded_file: Gemini file object.

        Returns:
            Time in seconds until expiration.
        """
        now = datetime.now(timezone.utc)
        return (uploaded_file.expiration_time - now).total_seconds()

    @staticmethod
    def split_and_label_prompt_parts_from_string(input_string: str) -> list[dict[str, str]]:
        """
        Split a string into labeled prompt parts (text vs. multimodal).

        Uses brackets to detect multimodal parts like [file.png].

        Args:
            input_string: The combined prompt string.

        Returns:
            A list of dictionaries with 'type' and 'value' keys.
        """
        pattern = r"\[([^\]]+)\]|([^[\]]+)"
        matches = re.findall(pattern, input_string)
        result = []

        for file, text in matches:
            if file:
                result.append({"type": "multimodal", "value": file.strip()})
            elif text.strip():
                result.append({"type": "text", "value": text.strip()})

        return result

    @staticmethod
    def has_complete_type_hints(func: typing.Callable) -> bool:
        """
        Verify that a function has type hints for all arguments and the return type.

        Args:
            func: The function to inspect.

        Returns:
            True if complete type hints are present.

        Raises:
            TypeError: If any parameter or the return type lacks a type hint.
        """
        sig = inspect.signature(func)
        for name, param in sig.parameters.items():
            if param.annotation is inspect.Parameter.empty:
                raise TypeError(f"Parameter '{name}' is missing a type hint.")

        if sig.return_annotation is inspect.Signature.empty:
            raise TypeError("Return type is missing a type hint.")

        return True

    @staticmethod
    def func_to_pydantic(func: typing.Callable) -> type[BaseModel]:
        """
        Convert a Python function into a Pydantic model representing its parameters.

        Args:
            func: The target function.

        Returns:
            A Pydantic BaseModel subclass.
        """
        model_fields = {}
        params = inspect.signature(func).parameters

        for name, param in params.items():
            if name == "self":
                continue

            annotation = param.annotation if param.annotation != inspect.Parameter.empty else typing.Any
            default = None if param.default == inspect.Parameter.empty else param.default
            description = ""

            # Handle Annotated type
            origin = typing.get_origin(annotation)
            args = typing.get_args(annotation)
            if origin is typing.Annotated and len(args) >= 2:
                annotation = args[0]
                description = args[1]

            model_fields[name] = (
                annotation,
                Field(default, description=description),
            )

        model_name = func.__name__
        model_doc = func.__doc__ or ""
        return create_model(model_name, __doc__=model_doc, **model_fields)

    @classmethod
    def func_to_tool(cls, func: typing.Callable) -> FunctionDeclaration:
        """
        Convert a Python function into a Gemini-compatible FunctionDeclaration.

        Args:
            func: The target function.

        Returns:
            A FunctionDeclaration object.
        """
        schema = cls.func_to_pydantic(func).schema()
        properties = schema.get("properties", {})

        return FunctionDeclaration(
            name=func.__name__,
            description=func.__doc__,
            parameters={
                "type": "object",
                "properties": {
                    name: {
                        "type": value.get("type", "string"),
                        "description": value.get("description", "")
                    }
                    for name, value in properties.items()
                }
            }
        )

    @staticmethod
    def normalize_prompt(prompt: typing.Any) -> list:
        """
        Normalize prompt inputs into a consistent list format.

        Args:
            prompt: Can be a string, Document, File, Image, or a custom MultimodalPart.

        Returns:
            A list of normalized prompt components.

        Raises:
            ValueError: If an unknown type is encountered.
        """
        from geminiplayground.parts import MultimodalPart

        if isinstance(prompt, str):
            prompt = [prompt]

        normalized = []

        for part in prompt:
            if isinstance(part, str):
                normalized.append(part)
            elif isinstance(part, MultimodalPart):
                normalized.extend(LibUtils.normalize_prompt(part.content_parts()))
            elif isinstance(part, Document):
                normalized.append(part.page_content)
            elif isinstance(part, (File, Image)):
                normalized.append(part)
            else:
                raise ValueError(f"Unsupported prompt part: {part}")

        return normalized
