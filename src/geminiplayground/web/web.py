import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.concurrency import run_in_threadpool
from fastapi.websockets import WebSocket, WebSocketDisconnect
import logging

from fastapi.staticfiles import StaticFiles

from geminiplayground.core import GeminiPlayground, ToolCall
from geminiplayground.web.utils import get_parts_from_prompt_text

logger = logging.getLogger(__name__)
web = FastAPI()

ROOT_DIR = Path(__file__).resolve().parent
FILES_DIR = Path(ROOT_DIR, "files")
TEMPLATES_DIR = Path(ROOT_DIR, "templates")
STATIC_DIR = Path(ROOT_DIR, "static")


@web.get("/files", response_class=HTMLResponse)
def list_files(request: Request) -> HTMLResponse:
    """
    Render an HTML page listing the files in the FILES_DIR directory.
    """
    try:
        files = sorted(f.name for f in FILES_DIR.iterdir() if f.is_file())
        file_urls = [f"{request.url}/{file}" for file in files]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {e}")

    return Jinja2Templates(TEMPLATES_DIR).TemplateResponse(
        request=request,
        name="files.html",
        context={"files": file_urls},
    )


@web.get("/files/{file_name}")
def get_file(file_name: str) -> FileResponse:
    """
    Return the requested file as a download.
    """
    file_path = FILES_DIR / file_name

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)


async def dispatch_event(websocket: WebSocket, event_type, data=None):
    """
    Dispatch websocket event
    """
    await websocket.send_json({"event": event_type, "data": data})


@web.websocket("/ws")
async def websocket_receiver(ws: WebSocket):
    """
    Websocket receiver
    """
    try:
        await ws.accept()
        chat = None
        logger.info(f"Websocket connected to {chat}")
        while True:
            data = await ws.receive_json()
            event = data.get("event")
            data = data.get("data")

            match event:
                case "clear_queue":
                    if chat:
                        chat.reset_chat()
                case "generate_response":
                    try:
                        generate_prompt = data.get("message")
                        generate_settings = data.get("settings", None)
                        model = generate_settings.get("model", None)
                        if model is None:
                            raise ValueError("Model not specified")
                        if chat is None or chat.model != model:
                            playground = GeminiPlayground(model=model)
                            chat = playground.start_chat()
                        prompt_parts = await get_parts_from_prompt_text(generate_prompt)
                        generate_response = await run_in_threadpool(chat.send_message, prompt_parts)
                        await dispatch_event(ws, "response_started")
                        for message_chunk in generate_response:
                            if isinstance(message_chunk, ToolCall):
                                await dispatch_event(ws, "response_chunk",
                                                     f"Calling function ...{message_chunk.tool_name}")
                                break
                            await dispatch_event(ws, "response_chunk", message_chunk.text)
                        await dispatch_event(ws, "response_completed")
                    except Exception as e:
                        logger.error(e)
                        await dispatch_event(ws, "response_error", {"message": str(e)})
                case _:
                    pass

    except WebSocketDisconnect:
        logger.warning("client disconnected ...")


os.environ["FILES_DIR"] = str(FILES_DIR)
os.environ["TEMPLATES_DIR"] = str(TEMPLATES_DIR)
web.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
web.mount("/files", StaticFiles(directory=FILES_DIR), name="files")
