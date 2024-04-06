from rich import print

from geminiplayground import GeminiClient

if __name__ == "__main__":
    gemini_client = GeminiClient()
    models = gemini_client.query_models()
    print(models)
