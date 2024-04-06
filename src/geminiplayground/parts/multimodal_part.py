import json
from abc import ABC, abstractmethod


class MultimodalPart(ABC):

    @property
    def files(self):
        """
        Get the files of the multimodal part
        :return:
        """
        raise NotImplementedError

    def upload(self):
        """
        Upload the multimodal part
        :return:
        """
        raise NotImplementedError

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
