import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .api import api
from .db.orm_utils import create_db, drop_db
from .ui import ui

BASE_DIR = Path(__file__).resolve().parent
FILES_DIR = Path(BASE_DIR, "files")
templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))

os.environ["FILES_DIR"] = FILES_DIR.as_posix()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Api life span
    :return:
    """
    print("ui is starting")
    drop_db()
    create_db()
    yield
    print("ui is shutting down")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:8001",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/files", StaticFiles(directory=FILES_DIR), name="files")


@app.get("/files", response_class=HTMLResponse)
def list_files(request: Request):
    files = os.listdir(FILES_DIR)
    files_paths = sorted([f"{request.url._url}/{f}" for f in files])
    return templates.TemplateResponse(
        request=request, name="files.html", context={"files": files_paths}
    )


apps = {
    "/api": api,
    "/": ui,
}
for path, sub_app in apps.items():
    app.mount(path, sub_app)
