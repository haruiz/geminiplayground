from time import sleep

from geminiplayground.core import GeminiClient
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

if __name__ == "__main__":
    model = "models/gemini-1.5-flash-001"
    gemini_client = GeminiClient()

    chat_history = [
        {
            "role": "user",
            "parts": [{"text": "My name is John. I am a software engineer."}],
        }
    ]
    with gemini_client.start_chat(model=model, history=chat_history) as chat:
        while True:
            user_input = input("You: ")
            if user_input == "exit":
                print(chat.history)
                break
            try:
                sleep(0.5)
                response = chat.generate_response(user_input, stream=True)
                for message_chunk in response:
                    print(message_chunk.text, end="")
            except Exception as e:
                print("Something went wrong: ", e)
                break
