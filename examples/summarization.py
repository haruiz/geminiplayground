from rich import print

from geminiplayground.parts import VideoFile, GitRepo, ImageFile, AudioFile, PdfFile
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

if __name__ == '__main__':
    my_content = [
        VideoFile("./../data/transformers-explained.mp4"),
        ImageFile("./../data/dog.jpg"),
        PdfFile("./../data/vis-language-model.pdf"),
        AudioFile("./../data/audio_example.mp3"),
        GitRepo.from_url(
            "https://github.com/karpathy/ng-video-lecture",
            branch="master",
            config={
                "content": "code-files"
            },
        )
    ]
    for content in my_content:
        response = content.summarize(model="models/gemini-1.5-flash-latest", stream=True)
        # print(response.text)
        for message_chunk in response:
            print(message_chunk.text, end="")
