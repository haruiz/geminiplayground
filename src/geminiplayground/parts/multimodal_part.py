import json
from abc import ABC, abstractmethod


class MultimodalPart(ABC):
    """
    Abstract class for multimodal part
    """

    @property
    def files(self):
        """
        Get the files of the multimodal part
        :return:
        """
        return []

    def clear_cache(self):
        """
        Clear the cache of the multimodal part
        :return:
        """
        ...

    def upload(self):
        """
        Upload the multimodal part
        :return:
        """
        ...

    @abstractmethod
    def content_parts(self, **kwargs):
        """
        transform a multimodal part into a list of content parts
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    def __str__(self):
        content_parts = self.content_parts()
        json_parts = [part.json() for part in content_parts]
        return json.dumps(json_parts, indent=4)
