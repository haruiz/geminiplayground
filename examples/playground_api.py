from dotenv import load_dotenv, find_dotenv

from geminiplayground.core import GeminiPlayground, ToolCall

load_dotenv(find_dotenv())

if __name__ == "__main__":
    playground = GeminiPlayground(
        model="models/gemini-1.5-flash-latest"
    )


    @playground.tool
    def subtract(a: int, b: int) -> int:
        """This function only subtracts two numbers"""
        return a - b


    @playground.tool
    def write_poem(about: str) -> str:
        """write a poem
        @param about: the subject of the poem
        """
        return "Roses are red, violets are blue, sugar is sweet, and so are you."


    chat = playground.start_chat(history=[])
    while True:
        user_input = input("You: ")
        if user_input == "exit":
            break
        try:
            model_response = chat.send_message(user_input)
            for response_chunk in model_response:
                print(response_chunk.text, end="")
            print()
        except Exception as e:
            print("Something went wrong: ", e)
            break
