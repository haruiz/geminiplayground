from dotenv import load_dotenv, find_dotenv

from geminiplayground.core import GeminiPlayground, Message

load_dotenv(find_dotenv())

if __name__ == "__main__":
    playground = GeminiPlayground(
        model="models/gemini-1.5-flash-latest"
    )


    @playground.tool
    def subtract(a: int, b: int) -> int:
        """return a - b, the difference between a and b"""
        return a - b


    @playground.tool
    def write_poem() -> str:
        """write a poem"""
        return "Roses are red, violets are blue, sugar is sweet, and so are you."


    chat = playground.start_chat(history=[])

    image = "https://images.unsplash.com/photo-1630484163294-4b3b3b3b3b3b"
    chat.send_message(["can you describe this image: ", ], stream=True)

    while True:
        user_input = input("You: ")
        if user_input == "exit":
            print(chat.history)
            break
        try:
            model_response = chat.send_message(user_input, stream=True)
            for response_chunk in model_response:
                if isinstance(response_chunk, Message):
                    print(response_chunk.text, end="")
                else:
                    print(
                        f"Tool: {response_chunk.tool_name}, "
                        f"Result: {response_chunk.tool_result}"
                    )
            print()
        except Exception as e:
            print("Something went wrong: ", e)
            break
