from geminiplayground import GeminiClient

if __name__ == '__main__':
    gemini_client = GeminiClient()
    files = gemini_client.query_files()
    gemini_client.delete_files(*files)
