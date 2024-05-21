from dotenv import find_dotenv
from dotenv import load_dotenv
from geminiplayground import GeminiClient
from rich import print

load_dotenv(find_dotenv())
if __name__ == "__main__":
    gemini_client = GeminiClient()
    files = gemini_client.query_files()
    print(files)
