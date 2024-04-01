from rich import print

from geminiplayground import GeminiClient

if __name__ == '__main__':
    gemini_client = GeminiClient()
    files = gemini_client.query_files()
    print(files)
