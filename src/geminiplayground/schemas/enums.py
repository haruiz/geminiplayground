from enum import Enum


class HarmCategory(str, Enum):
    SEXUALLY_EXPLICIT = "HARM_CATEGORY_SEXUALLY_EXPLICIT"
    HATE_SPEECH = "HARM_CATEGORY_HATE_SPEECH"
    HARASSMENT = "HARM_CATEGORY_HARASSMENT"
    DANGEROUS_CONTENT = "HARM_CATEGORY_DANGEROUS_CONTENT"


class HarmBlockThreshold(str, Enum):
    HARM_BLOCK_THRESHOLD_UNSPECIFIED = "HARM_BLOCK_THRESHOLD_UNSPECIFIED"
    BLOCK_LOW_AND_ABOVE = (
        "BLOCK_LOW_AND_ABOVE"  # Content with NEGLIGIBLE will be allowed.
    )
    BLOCK_MEDIUM_AND_ABOVE = (
        "BLOCK_MEDIUM_AND_ABOVE"  # Content with NEGLIGIBLE and LOW will be allowed.
    )
    BLOCK_ONLY_HIGH = (
        "BLOCK_ONLY_HIGH"  # Content with NEGLIGIBLE, LOW, and MEDIUM will be allowed.
    )
    BLOCK_NONE = "BLOCK_NONE"  # All content will be allowed.


class HarmProbability(str, Enum):
    NEGLIGIBLE = "NEGLIGIBLE"  # Content has a negligible chance of being unsafe.
    LOW = "LOW"  # Content has a low chance of being unsafe.
    MEDIUM = "MEDIUM"  # Content has a medium chance of being unsafe.
    HIGH = "HIGH"  #
