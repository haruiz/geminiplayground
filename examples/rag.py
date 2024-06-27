from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_weaviate import WeaviateVectorStore

from geminiplayground.parts import MultimodalPart, ImageFile, AudioFile, GitRepo, PdfFile, VideoFile
from langchain_core.retrievers import BaseRetriever
from dotenv import load_dotenv, find_dotenv
from geminiplayground.rag import SummarizationLoader, AgenticToolUseRAG
from rich.console import Console
from langchain_core.vectorstores import VectorStore
import typing
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
import weaviate

# from geminiplayground.catching import cache

console = Console()

load_dotenv(find_dotenv())


class MultiModalSummarizationRetriever(BaseRetriever):
    summarization_model: str
    docs: typing.List[MultimodalPart]
    vectorstore: VectorStore
    batch_docs_size = 50
    """List of documents to retrieve from."""
    k: int
    """Number of top results to return"""

    def index_docs(self):
        """
        Index all the documents.
        """
        loader = SummarizationLoader(self.summarization_model, *self.docs)
        docs = loader.load()
        self.vectorstore.add_documents(docs, batch_size=self.batch_docs_size)

    def _get_relevant_documents(
            self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> typing.List[Document]:
        docs, scores = zip(
            *self.vectorstore.similarity_search_with_score(query, k=self.k)
        )
        for doc, score in zip(docs, scores):
            doc.metadata["score"] = score

        return docs


def create_retriever_from_multimodal_data(docs_index_name: str,
                                          docs: typing.List[MultimodalPart]):
    """
    Create a retriever for a document
    """
    return MultiModalSummarizationRetriever(
        docs=docs,
        summarization_model="models/gemini-1.5-flash-latest",
        vectorstore=WeaviateVectorStore(
            client=weaviate_client,
            index_name=docs_index_name,
            embedding=embeddings_model,
            text_key="page_content"
        ),
        k=5
    )


if __name__ == '__main__':

    weaviate_client = weaviate.connect_to_embedded()
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", task_type="retrieval_document")
    chat_model = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash-latest", temperature=0.0)

    retrievers = [{
        "name": "media_files",
        "description": "This Retriever combine a various media files, including a picture of my dog",
        "retriever": create_retriever_from_multimodal_data("media_files", [
            ImageFile("./../data/dog.jpg"),

        ])
    }, {
        "name": "code_files",
        "description": "This Retriever contains code from karpathy's ng-video-lecture repo about transformers",
        "retriever": create_retriever_from_multimodal_data("code_files", [
            GitRepo.from_url(
                "https://github.com/karpathy/ng-video-lecture",
                branch="master",
                config={
                    "content": "code-files"
                },
            )])
    }, {
        "name": "transformer_files",
        "description": "This Retriever contains various media files, relating to transformers and language models",
        "retriever": create_retriever_from_multimodal_data("pdf_files", [
            VideoFile("./../data/transformers-explained.mp4"),
            PdfFile("./../data/vis-language-model.pdf"),
            AudioFile("./../data/audio_example.mp3")
        ])
    }]

    # Index all the documents in the retrievers
    for retriever in retrievers:
        retriever["retriever"].index_docs()


    # rag = LOTRRAG(
    #     chat_model=chat_model,
    #     retrievers_info=retrievers,
    #     chat_history=[]
    # )

    # rag = AgenticRoutingRAG(
    #     chat_model=chat_model,
    #     retrievers_info=retrievers,
    #     chat_history=[]
    # )

    @tool
    def subtract(x: float, y: float) -> float:
        """Subtract 'x' from 'y'."""
        return y - x


    @tool
    def add(x: float, y: float) -> float:
        """ Add 'x' and 'y'."""
        return x + y


    rag = AgenticToolUseRAG(
        chat_model=chat_model,
        retrievers_info=retrievers,
        custom_tools=[subtract, sum],
        chat_history=[])

    while True:
        question = input("Question: ")
        if question.lower() == "exit":
            print(rag.chat_history)
            weaviate_client.close()
            break
        result = rag.invoke(question)
        rag.chat_history.extend([HumanMessage(content=question), result.answer])
        console.print(f"Answer: {result.answer}")
        docs = result.docs
        for doc in docs[:3]:
            console.print(doc.page_content[:100], doc.metadata)
