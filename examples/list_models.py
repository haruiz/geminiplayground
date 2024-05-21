from dotenv import find_dotenv
from dotenv import load_dotenv
from geminiplayground import GeminiClient
from rich import print

load_dotenv(find_dotenv())

if __name__ == "__main__":
    gemini_client = GeminiClient()
    models = gemini_client.query_models()
    print(models)
