import json
from abc import ABC, abstractmethod


class MultimodalPart(ABC):
    """
    Abstract class for multimodal part
    """

    @abstractmethod
    def content_parts(self, **kwargs):
        """
        transform a multimodal part into a list of content parts
        :param kwargs:
        :return:
        """
        raise NotImplementedError
