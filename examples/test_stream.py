import json
from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests

url = "http://localhost:8081/api/generateStream"
headers = {'Content-Type': 'application/json'}
# Convert data to JSON format
data = {
    'message': "Hi!, how are you doing?, can you write a poem?",
    'model': "models/gemini-1.0-pro-latest"
}

# Set the Content-Type header to application/json
with requests.post(url, data=json.dumps(data), stream=True, headers=headers) as r:
    for chunk in r.iter_content(None, decode_unicode=True):
        if chunk:
            print(chunk, end='', flush=True)
