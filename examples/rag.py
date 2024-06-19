# from geminiplayground.rag import AgenticRoutingRAG
# import google.generativeai as genai
# import os
#
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# rag = SummarizationRAG(
#     summarization_model="models/gemini-1.5-flash-latest",
#     chat_model="models/gemini-1.5-flash-latest",
#     embeddings_model="models/embedding-001"
# )
# files = [
#     # "./data/vis-language-model.pdf",
#     "./data/transformers-explained.mp4",
# ]
# for file in files:
#     rag.add_file(file)
# # rag.clear_index()
# rag.index_docs()
# rag.chat()

# rag = AgenticRoutingRAG(
#     summarization_model="models/gemini-1.5-flash-latest",
#     chat_model="models/gemini-1.5-flash-latest",
#     embeddings_model="models/embedding-001"
# )
# files = [
#     "./../data/vis-language-model.pdf",
#     "./../data/transformers-explained.mp4",
# ]
# for file in files:
#     rag.add_file(file)
# rag.index_docs()
# rag.chat()
