import json
from abc import ABC, abstractmethod


class MultimodalPart(ABC):
    @abstractmethod
    def content_parts(self, **kwargs):
        raise NotImplementedError

    def __str__(self):
        content_parts = self.content_parts()
        json_parts = [part.json() for part in content_parts]
        return json.dumps(json_parts, indent=4)
