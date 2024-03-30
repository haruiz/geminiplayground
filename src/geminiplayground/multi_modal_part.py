from abc import ABC, abstractmethod


class MultimodalPart(ABC):
    @abstractmethod
    def content_parts(self, **kwargs):
        raise NotImplementedError
