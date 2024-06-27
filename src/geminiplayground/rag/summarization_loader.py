from typing import Iterator

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from geminiplayground.parts import MultiModalPartFile, MultimodalPart


class SummarizationLoader(BaseLoader):

    def __init__(self, model: str, *content: MultimodalPart):
        self._content = content
        self._model = model

    def lazy_load(self) -> Iterator[Document]:
        """
        Lazy load documents.
        """
        for content in self._content:
            if isinstance(content, MultiModalPartFile):
                yield self._create_document_from_file(content)
            else:
                for part in content.content_parts():
                    if isinstance(part, MultiModalPartFile):
                        yield self._create_document_from_file(part)
                    elif isinstance(part, Document):
                        yield part

    def _create_document_from_file(self, part: MultiModalPartFile) -> Document:
        """
        Create a Document object from a MultiModalPartFile.
        """
        try:
            file_summary = part.summarize(model=self._model, stream=False)
            return Document(
                page_content=file_summary,
                metadata={"file_path": str(part.local_path)}
            )
        except Exception as ex:
            raise ValueError(f"Error summarizing file {part.local_path}: {ex}") from ex
