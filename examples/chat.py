from time import sleep

from geminiplayground.core import GeminiClient
from geminiplayground.schemas import ChatHistory, TextPart, ChatMessage
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

if __name__ == '__main__':
    model = "models/gemini-1.5-pro-latest"
    gemini_client = GeminiClient()

    chat_history = ChatHistory(messages=[
        ChatMessage(role="user", parts=[TextPart(text="Write a poem about the ocean")]),
    ])
    with gemini_client.start_chat(model=model, history=chat_history) as chat:
        while True:
            user_input = input("You: ")
            if user_input == "exit":
                print(chat.history)
                break
            try:
                sleep(0.5)
                response = chat.send_message(user_input, stream=True, timeout=0.5)
                for candidate in response:
                    print(candidate.text)
            except Exception as e:
                print("Something went wrong: ", e)
                break
