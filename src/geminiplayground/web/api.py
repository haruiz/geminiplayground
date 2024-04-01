import os
from pathlib import Path
from typing import List

import validators
from PIL import Image as PILImage
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi import File, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from geminiplayground import GeminiClient, ImageFile, VideoFile, GitRepo
from geminiplayground.utils import get_gemini_playground_cache_dir, rm_tree
from .db.models import *
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
async def upload_file(request: Request, upload_file: UploadFile = File(alias="file"),
                      display_name: str = Form(alias="displayName", default=None)):
    """
    Hello endpoint
    :return:
    """
    cache_dir = get_gemini_playground_cache_dir()
    public_files_dir = Path(os.environ.get("FILES_DIR", cache_dir))

    content_type = upload_file.content_type
    # check if the content type is an image or a video
    is_image = content_type.startswith("image/")
    is_video = content_type.startswith("video/")

    # create the directory to store the files if it does not exist
    assert any([is_image, is_video]), f"Unsupported content type: {content_type}"
    out_dir = cache_dir / "images" if is_image else cache_dir / "videos"
    out_dir.mkdir(parents=True, exist_ok=True)

    # save file to disk
    file_path = out_dir / upload_file.filename
    with file_path.open("wb") as f:
        f.write(upload_file.file.read())

    if is_image:
        multimodal_part = ImageFile(
            image_path=str(file_path),
            gemini_client=gemini_client
        )
        file_info = multimodal_part.upload()
        files_info = [file_info]
        file_thumbnail_img = PILImage.open(str(file_path))
        file_thumbnail_path = public_files_dir / f"thumbnail_{file_path.name}"
    else:
        multimodal_part = VideoFile(
            video_path=str(file_path),
            gemini_client=gemini_client
        )
        _, files_info = multimodal_part.upload()
        file_thumbnail_img = multimodal_part.extract_frame_at(5)
        file_thumbnail_path = public_files_dir / f"thumbnail_{file_path.stem}.jpg"
    db_session = SessionMaker()
    try:
        file_name = Path(multimodal_part.file_path).name
        part_db_entry = MultimodalPartEntry(
            name=file_name,
            content_type="image" if is_image else "video"
        )
        for file_info in files_info:
            file_db_entry = FileEntry(
                name=file_info.name,
                display_name=file_info.display_name,
                mime_type=content_type,
                uri=str(file_info.uri),
                part_id=part_db_entry.name
            )
            part_db_entry.files.append(file_db_entry)

        db_session.add(part_db_entry)
        file_thumbnail_img.thumbnail(THUMBNAIL_SIZE, PILImage.Resampling.NEAREST)
        file_thumbnail_img.save(file_thumbnail_path)
        db_session.commit()
        return JSONResponse(content={"message": "File uploaded successfully"})
    except Exception as e:
        db_session.rollback()
        raise e


@api.post("/uploadRepo")
async def upload_repo(request: Request):
    """
    Hello endpoint
    :return:
    """
    config = {
        "content": "code-files",  # "code-files" or "issues"
        "exclude_dirs": ["frontend", "ui"],
        "file_extensions": [".py"]
    }
    data = await request.json()
    repo_path = data.get("repoPath")

    if validators.url(repo_path):
        multimodal_part = GitRepo.from_repo_url(repo_path, config=config, branch="main")
    else:
        multimodal_part = GitRepo.from_folder(repo_path, config=config)
    db_session = SessionMaker()
    try:
        part_db_entry = MultimodalPartEntry(
            name=multimodal_part.repo_folder.name,
            content_type="repo"
        )
        db_session.add(part_db_entry)
        db_session.commit()
        return JSONResponse(content={"message": "Repo created successfully"})
    except Exception as e:
        db_session.rollback()
        raise e


class MultimodalPartEntrySchema(BaseModel):
    name: str = Field(..., description="The name of the multimodal part")
    content_type: str = Field(..., description="The type of the multimodal part")


@api.get("/parts")
async def get_parts() -> List[MultimodalPartEntrySchema]:
    """
    Hello endpoint
    :return:
    """
    session = SessionMaker()
    parts = session.query(MultimodalPartEntry).all()
    return parts


async def delete_part_files_from_server(files: List[FileEntry]):
    """
    Delete files from the server
    :param files:
    :return:
    """
    gemini_client.delete_files([file.name for file in files])


async def delete_files_from_disk(part: MultimodalPartEntry):
    """
    Delete files from the disk
    :param part:  The part to delete
    :return:
    """
    cache_dir = get_gemini_playground_cache_dir()
    public_files_dir = Path(os.environ.get("FILES_DIR", cache_dir))
    # delete thumbnail
    thumbnail_path = public_files_dir / f"thumbnail_{part.name}"
    if thumbnail_path.exists():
        thumbnail_path.unlink()
    # delete files
    if part.content_type == "image":
        file_path = cache_dir / "images" / part.name
        file_path.unlink()
    elif part.content_type == "video":
        video_file = cache_dir / "videos" / part.name
        if video_file.exists():
            video_file.unlink()
        video_folder = cache_dir / "videos" / Path(part.name).stem
        rm_tree(video_folder)
    elif part.content_type == "repo":
        repo_folder = cache_dir / "repos" / part.name
        rm_tree(repo_folder)


@api.delete("/parts/{part_id}")
async def delete_part(part_id: str, background_tasks: BackgroundTasks):
    """
    Hello endpoint
    :return:
    """
    session = SessionMaker()
    try:
        part = session.query(MultimodalPartEntry).filter_by(name=part_id).first()
        if part:
            session.delete(part)
            session.commit()
            background_tasks.add_task(delete_part_files_from_server, part.files)
            background_tasks.add_task(delete_files_from_disk, part)
            return JSONResponse(content={"message": "Part deleted successfully"})
        return JSONResponse(content={"message": "Part not found"}, status_code=404)
    except Exception as e:
        session.rollback()
        raise e
