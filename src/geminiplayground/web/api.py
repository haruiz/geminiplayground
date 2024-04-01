import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi import File, UploadFile
from fastapi.responses import JSONResponse

from geminiplayground.core import GeminiClient
from geminiplayground.parts import MultimodalPartFactory
from geminiplayground.utils import get_gemini_playground_cache_dir, TemporaryFile
from .db.models import MultimodalPartEntry, FileEntry
from .db.orm_session import SessionMaker

api = FastAPI(root_path="/api")
gemini_client = GeminiClient()

THUMBNAIL_SIZE = (64, 64)


@api.get("/")
def root():
    """
    Root endpoint
    :return:
    """
    return JSONResponse(content={"content": "Hi from the Api"})


@api.post("/uploadFile")
async def upload_file(request: Request, upload_file: UploadFile = File(alias="file")):
    """
    Hello endpoint
    :return:
    """

    mime_type = upload_file.content_type
    public_files_dir = Path(os.environ["FILES_DIR"])
    supported_content_types = ["image/png", "image/jpeg", "image/jpg", "video/mp4"]
    if mime_type not in supported_content_types:
        return JSONResponse(content={"error": f"Unsupported content type: {mime_type}"})
    content_type = {
        "image/png": "image",
        "image/jpeg": "image",
        "image/jpg": "image",
        "video/mp4": "video",
    }[mime_type]

    file_name = upload_file.filename
    file_ext = Path(file_name).suffix
    with TemporaryFile(suffix=file_ext) as file_path:
        with open(file_path, "wb") as f:
            f.write(upload_file.file.read())

        multimodal_part = MultimodalPartFactory.from_path(file_path)
        part_thumbnail = multimodal_part.thumbnail(THUMBNAIL_SIZE)
        part_thumbnail_path = Path(public_files_dir).joinpath(f"thumbnail_{file_name}.png")
        part_thumbnail.save(part_thumbnail_path)

        session = SessionMaker()
        try:
            multimodal_part_db_entry = MultimodalPartEntry(
                name=file_name,
                content_type=content_type
            )
            # for part_file in multimodal_part.files:
            #     file_db_entry = FileEntry(
            #         name=part_file.name,
            #         mime_type=part_file.mime_type,
            #         uri=str(part_file.uri),
            #         part_id=file_name
            #     )
            #     multimodal_part_db_entry.files.append(file_db_entry)
            # session.add(multimodal_part_db_entry)
            # session.commit()
        except Exception as e:
            session.rollback()
            return JSONResponse(content={"error": str(e)})

    return JSONResponse(content={"content": "File uploaded"})
