from dotenv import find_dotenv
from dotenv import load_dotenv
from geminiplayground.core import GeminiClient
from geminiplayground.parts import PdfFile
from geminiplayground.schemas import GenerateRequest
from geminiplayground.schemas import GenerateRequestParts
from geminiplayground.schemas import TextPart
from rich import print

load_dotenv(find_dotenv())


def chat_wit_your_pdf():
    """
    Get the content parts of a pdf file and generate a request.
    :return:
    """
    gemini_client = GeminiClient()
    model = "models/gemini-1.5-pro-latest"

    pdf_file_path = "https://www.tnstate.edu/faculty/fyao/COMP3050/Py-tutorial.pdf"
    pdf_file = PdfFile(pdf_file_path, gemini_client=gemini_client)
    pdf_text = pdf_file.files
    print("pdf text: ", pdf_text)

    pdf_parts = pdf_file.content_parts()
    print("pdf parts: ", pdf_parts)
    request_parts = GenerateRequestParts(
        parts=[
            TextPart(text="Please create code smippet del pdf :"),
            *pdf_parts,
        ]
    )
    request = GenerateRequest(
        contents=[request_parts],
    )
    tokens_count = gemini_client.get_tokens_count(model, request)
    print("Tokens count: ", tokens_count)
    response = gemini_client.generate_response(model, request)

    # Print the response
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.text:
                print(part.text)


if __name__ == "__main__":
    chat_wit_your_pdf()
