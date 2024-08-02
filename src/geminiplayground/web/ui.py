import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

ui = FastAPI(root_path="")

root_file_path = os.path.dirname(os.path.abspath(__file__))
static_folder_root = os.path.join(root_file_path, "static")

ui.mount("/", StaticFiles(directory=static_folder_root, html=True), name="static")

import os

from fastapi import FastAPI
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FILES_DIR = Path(BASE_DIR, "files")
TEMPLATES_DIR = Jinja2Templates(directory=str(Path(BASE_DIR, "templates")))

app = FastAPI()


@app.get("/files", response_class=HTMLResponse)
def list_files(request: Request):
    files = os.listdir(FILES_DIR)
    files_paths = sorted([f"{request.url._url}/{f}" for f in files])
    return TEMPLATES_DIR.TemplateResponse(
        request=request, name="files.html", context={"files": files_paths}
    )


root_file_path = os.path.dirname(os.path.abspath(__file__))
static_folder_root = os.path.join(root_file_path, "static")
app.mount("/", StaticFiles(directory=static_folder_root, html=True), name="static")
app.mount("/files", StaticFiles(directory=FILES_DIR), name="files")
