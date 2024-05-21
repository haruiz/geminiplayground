from dotenv import find_dotenv
from dotenv import load_dotenv
from geminiplayground import GeminiClient

load_dotenv(find_dotenv())

if __name__ == "__main__":
    gemini_client = GeminiClient()
    files = gemini_client.query_files()
    gemini_client.delete_files(*files)
