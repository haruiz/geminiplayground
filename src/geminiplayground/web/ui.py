import os

from fastapi import FastAPI
from fastapi.responses import JSONResponse

ui = FastAPI(root_path="")

root_file_path = os.path.dirname(os.path.abspath(__file__))
static_folder_root = os.path.join(root_file_path, "static")


@ui.get("/")
def root():
    """
    Root endpoint
    :return:
    """
    return JSONResponse(content={"content": "Hi from the web UI"})
