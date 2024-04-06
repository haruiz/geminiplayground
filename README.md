## Gemini Playground

![Gemini Logo](https://raw.githubusercontent.com/haruiz/geminiplayground/main/images/logo.png)

Gemini-Playground provides a Python interface and a UI to interact with last Google's
Gemini's version, `models/gemini-1.5-pro-latest`. With Gemini Playground,
you can:

* **Engage in conversation with your data:** Upload images, and videos using a simple API and
  generate responses based on your prompts.
* **Chat with your codebase:** Ask Gemini to analyze your code, explain its
  functionality, suggest improvements, or even write documentation for it.
* **Explore multimodal capabilities:** Combine different data types in your prompts,
  like asking Gemini to describe what's happening in a video and an image simultaneously.

### Features

* **Intuitive API:** The `GeminiClient` class offers a simple and
  easy-to-use interface for interacting with the Gemini API.
* **Multimodal Support:** Upload and use text, images, videos, and
  code in your prompts.
* **File Management:** Upload, list, and remove files from your
  Gemini storage.
* **Token Counting:** Estimate the number of tokens required for a
  prompt and response.
* **Response Generation:** Generate responses from Gemini based on
  your prompts and uploaded content.
* **Rich Logging:** Get informative and colorful logging messages for
  better understanding of the process.

### Installation

```bash
pip install -i https://test.pypi.org/simple/ geminiplayground
```

### Usage

1. **Set up your API key:**
    * Obtain an API key from Google AI-Studio.
    * Set the `AISTUDIO_API_KEY` environment variable with your API
      key.

2. **Create a `GeminiClient` instance:**

```python
from geminiplayground.core import GeminiClient
from geminiplayground.parts import VideoFile, ImageFile
from geminiplayground.schemas import HarmCategory, HarmBlockThreshold

gemini_client = GeminiClient()
```

3. **Upload files:**

```python

video_file_path = "BigBuckBunny_320x180.mp4"
video_file = VideoFile(video_file_path, gemini_client=gemini_client)
video_file.upload()

image_file_path = "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
image_file = ImageFile(image_file_path, gemini_client=gemini_client)
image_file.upload()
```

4. **Create a prompt:**

```python
multimodal_prompt = [
    "See this video",
    video_file,
    "and this image",
    image_file,
    "Explain what you see."
]
```

5. **Generate a response:**

```python
response = gemini_client.generate_response("models/gemini-1.5-pro-latest", multimodal_prompt,
                                           generation_config={"temperature": 0.0, "top_p": 1.0},
                                           safety_settings={
                                               "category": HarmCategory.DANGEROUS_CONTENT,
                                               "threshold": HarmBlockThreshold.BLOCK_NONE
                                           })

# Print the response
for candidate in response.candidates:
    for part in candidate.content.parts:
        if part.text:
            print(part.text)
```

```text
The video is a short animated film called "Big Buck Bunny." It is a comedy about a large, white rabbit 
who is bullied by three smaller animals. The rabbit eventually gets revenge on his tormentors. The film 
was created using Blender, a free and open-source 3D animation software.

The image is of four dice, each a different color. The dice are transparent and have white dots. The 
image is isolated on a black background.
```

6. **You can also chat with your data:**

**Chat with your codebase:**

```python
from rich import print

from geminiplayground.core import GeminiClient
from geminiplayground.parts.git_repo_part import GitRepo
from geminiplayground.schemas import GenerateRequestParts, TextPart, GenerateRequest


def chat_wit_your_code():
    """
    Get the content parts of a github repo and generate a request.
    :return:
    """

    repo = GitRepo.from_repo_url("https://github.com/karpathy/ng-video-lecture",
                                 branch="master",
                                 config={
                                     "content": "code-files",  # "code-files" or "issues"
                                     "exclude_dirs": ["frontend", "ui"],
                                     "file_extensions": [".py"]
                                 })
    repo_parts = repo.content_parts()

    request_parts = GenerateRequestParts(parts=[
        TextPart(text="use this codebase:"),
        *repo_parts,
        TextPart(
            text="Help me to write a Readme file for this codebase."),
    ])
    request = GenerateRequest(
        contents=[
            request_parts
        ]
    )
    model = "models/gemini-1.5-pro-latest"
    gemini_client = GeminiClient()
    tokens_count = gemini_client.get_tokens_count(model, request)
    print("Tokens count: ", tokens_count)
    response = gemini_client.generate_response(model, request)

    # Print the response
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.text:
                print(part.text)


if __name__ == '__main__':
    chat_wit_your_code()

```

**Chat with your videos:**

```python
from rich import print

from geminiplayground.core import GeminiClient
from geminiplayground.parts import VideoFile
from geminiplayground.schemas import GenerateRequestParts, TextPart, GenerateRequest


def chat_wit_your_video():
    """
    Get the content parts of a video and generate a request.
    :return:
    """
    gemini_client = GeminiClient()
    model = "models/gemini-1.5-pro-latest"

    video_file_path = "./../data/BigBuckBunny_320x180.mp4"
    video_file = VideoFile(video_file_path, gemini_client=gemini_client)
    video_parts = video_file.content_parts()
    video_files = video_file.files[-4:]
    for part in video_parts[:5]:
        print(part)

    request_parts = GenerateRequestParts(parts=[
        TextPart(text="check this video?:"),
        *video_parts,
        TextPart(text="list the object you see in the video")
    ])
    request = GenerateRequest(
        contents=[
            request_parts
        ]
    )
    tokens_count = gemini_client.get_tokens_count(model, request)
    print("Tokens count: ", tokens_count)
    response = gemini_client.generate_response(model, request)

    # Print the response
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.text:
                print(part.text)


if __name__ == '__main__':
    chat_wit_your_video()

```

**Chat with your images:**

```python
from rich import print

from geminiplayground.core import GeminiClient
from geminiplayground.parts import ImageFile
from geminiplayground.schemas import GenerateRequestParts, TextPart, GenerateRequest


def chat_wit_your_images():
    """
    Get the content parts of an image and generate a request.
    :return:
    """
    gemini_client = GeminiClient()
    model = "models/gemini-1.5-pro-latest"

    image_file_path = "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
    image_file = ImageFile(image_file_path, gemini_client=gemini_client)
    image_parts = image_file.content_parts()
    image_files = image_file.files
    print("Image files: ", image_files)

    request_parts = GenerateRequestParts(parts=[
        TextPart(text="You see this image?:"),
        *image_parts,
        TextPart(text="Describe what you see"),
    ])
    request = GenerateRequest(
        contents=[
            request_parts
        ],

    )
    tokens_count = gemini_client.get_tokens_count(model, request)
    print("Tokens count: ", tokens_count)
    response = gemini_client.generate_response(model, request)

    # Print the response
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.text:
                print(part.text)


if __name__ == '__main__':
    chat_wit_your_images()
```

This is a basic example.Explore the codebase and documentation for more
advanced functionalities and examples.

### GUI

You can also use the GUI to interact with the API. To start the GUI, run:

```bash
geminiplayground ui
```

This will start a local server and open the GUI in your default browser.

![Gemini GUI](https://raw.githubusercontent.com/haruiz/geminiplayground/main/images/ui.png)

### Contributing

Contributions are welcome! Please see the`CONTRIBUTING.md` file for guidelines [Coming soon].

### License

This codebase is licensed under the MIT License.See the`LICENSE`file for details. [Coming soon].

