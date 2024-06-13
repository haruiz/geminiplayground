import typing

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.vectorstores import VectorStore


class ScoredRetriever(BaseRetriever):
    vectorstore: VectorStore
    """List of documents to retrieve from."""
    k: int
    """Number of top results to return"""

    def _get_relevant_documents(
            self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> typing.List[Document]:
        """Sync implementations for retriever."""
        """Get docs, adding score information."""
        docs, scores = zip(
            *self.vectorstore.similarity_search_with_score(query, k=self.k)
        )
        for doc, score in zip(docs, scores):
            print(f"Score: {score} for doc: {doc}")
            doc.metadata["score"] = score

        return docs
