import asyncio
import logging
import os
import shutil
from pathlib import Path
from typing import Annotated

import validators
from fastapi import FastAPI, WebSocket, Depends, Request, BackgroundTasks, HTTPException, WebSocketDisconnect, \
    UploadFile, File
from fastapi.responses import JSONResponse
from googleapiclient.errors import HttpError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.concurrency import run_in_threadpool
from geminiplayground.core import GeminiClient
from geminiplayground.parts import GitRepoBranchNotFoundException, GitRepo, MultimodalPartFactory, MultimodalPart
from geminiplayground.schemas import GenerationSettings
from geminiplayground.utils import get_repo_name, check_github_repo_branch_exists, \
    get_github_repo_available_branches, folder_contains_git_repo, get_gemini_playground_cache_dir, \
    create_image_thumbnail, create_video_thumbnail
from .db.models import MultimodalPartEntry as MultimodalPartDBModel, EntryStatus
from .db.session_manager import get_db_session
from .utils import get_parts_from_prompt_text

logger = logging.getLogger("rich")

api = FastAPI(root_path="/api")
gemini_client = GeminiClient()

THUMBNAIL_SIZE = (64, 64)
DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]


@api.get("/models")
def get_models_handler():
    """
    Get models
    :return:
    """
    models = gemini_client.query_models()
    models = list(sorted(models, key=lambda model: model.input_token_limit, reverse=True))
    return models


@api.get("/parts")
async def get_tags_handler(request: Request, db_session: DBSessionDep, background_tasks: BackgroundTasks):
    """
    Get tags
    :return:
    """
    query = select(MultimodalPartDBModel)
    result = await db_session.execute(query)
    return result.scalars().all()


@api.websocket("/ws")
async def websocket_receiver(websocket: WebSocket):
    try:
        await websocket.accept()
        chat_history = []

        async def dispatch_event(event_type, data=None):
            await websocket.send_json({"event": event_type, "data": data})

        while True:

            data = await websocket.receive_json()
            event = data.get("event")
            data = data.get("data")
            print(event)
            match event:
                case "generate_response":
                    generate_prompt = data.get("message")
                    generative_model = data.get("model")
                    generate_settings = data.get("settings", None)
                    try:
                        chat = gemini_client.start_chat(model=generative_model, history=chat_history)
                        prompt_parts = await get_parts_from_prompt_text(generate_prompt)
                        logger.info(f"Prompt parts: {len(prompt_parts)}")

                        generate_response = await run_in_threadpool(lambda: chat.generate_response(prompt_parts,
                                                                                                   stream=True,
                                                                                                   generation_config=GenerationSettings(
                                                                                                       **generate_settings)))

                        await dispatch_event("response_started")
                        for response_chunk in generate_response:
                            await dispatch_event("response_chunk", response_chunk.text)
                        await dispatch_event("response_completed")
                    except (HttpError, Exception) as e:
                        error_message = e.reason \
                            if hasattr(e, "reason") else e.message \
                            if hasattr(e, "message") else str(e)
                        logger.error(e)
                        await dispatch_event("response_error", {
                            "message": error_message
                        })

                case "clear_queue":
                    chat_history = []
                case _:
                    pass
    except WebSocketDisconnect as e:
        logger.error(e)


@api.get("/tags")
async def get_tags_handler(request: Request, db_session: DBSessionDep):
    """
    Get tags
    :return:
    """
    request_url = request.url._url
    base_url = request_url.split("/api")[0]
    files_url = f"{base_url}/files"
    query = select(MultimodalPartDBModel).where(MultimodalPartDBModel.status == EntryStatus.READY)
    result = await db_session.execute(query)
    parts = result.scalars().all()
    tags = []
    for part in parts:
        if part.content_type == "repo":
            thumbnail_url = f"{files_url}/thumbnail_github.png"
        elif part.content_type == "audio":
            thumbnail_url = f"{files_url}/thumbnail_audio.png"
        else:
            thumbnail_url = f"{files_url}/thumbnail_{Path(part.name).stem}.jpg"
        tags.append({
            "value": part.name,
            "name": part.name,
            "description": "",
            "icon": thumbnail_url,
            "type": part.content_type,
        })
    return tags


async def clone_repo_task(repo_name: str, repo_path: str, repo_branch: str):
    """
    Clone a repository
    """
    try:
        async for session in get_db_session():
            query = select(MultimodalPartDBModel).filter(MultimodalPartDBModel.name == repo_name)
            result = await session.execute(query)
            part = result.scalars().first()
            try:
                await run_in_threadpool(lambda: GitRepo.from_url(repo_path, branch=repo_branch))
                logger.info(f"Cloned repository {repo_name} from {repo_path} branch {repo_branch}")
                part.status = EntryStatus.READY
            except GitRepoBranchNotFoundException as e:
                part.status = EntryStatus.ERROR
                part.status_message = str(e)
                logger.error(f"Error cloning repository {repo_name} from {repo_path} branch {repo_branch}: {e}")
            finally:
                await session.commit()
    except Exception as e:
        logger.error(e)


@api.post("/uploadRepo")
async def upload_repo_handler(request: Request, background_tasks: BackgroundTasks, db_session: DBSessionDep):
    """
    Hello endpoint
    :return:
    """

    body_data = await request.json()
    repo_path = body_data.get("repoPath")
    repo_branch = body_data.get("repoBranch")

    try:
        if validators.url(repo_path):
            available_branches = get_github_repo_available_branches(repo_path)
            assert repo_branch in available_branches, f"Branch {repo_branch} does not exist in {repo_path}, " \
                                                      f"available branches are: {available_branches}"
        elif Path(repo_path).is_dir() and Path(repo_path).exists():
            assert folder_contains_git_repo(repo_path), f"Invalid repository path: {repo_path}"
        else:
            raise Exception(f"Invalid repository path: {repo_path}")
        repo_name = get_repo_name(repo_path)
        new_part = MultimodalPartDBModel(
            name=repo_name,
            content_type="repo"
        )
        db_session.add(new_part)
        await db_session.commit()
        if validators.url(repo_path):
            background_tasks.add_task(clone_repo_task, repo_name, repo_path, repo_branch)
    except Exception as e:
        raise HTTPException(status_code=500, detail=repr(e))
    return JSONResponse(content={"content": "Repository created"})


async def upload_file_task(file_path: Path, content_type: str):
    """
    Upload a file asynchronously with optimized session handling and thumbnail generation.
    """
    try:
        async for session in get_db_session():
            await upload_file(session, file_path, content_type)
    except Exception as e:
        logger.error(f"Failed to process file {file_path}: {str(e)}")


async def upload_file(session: AsyncSession, file_path: Path, content_type: str):
    """
    Upload a file handler
    @param session: The database session
    @param file_path: The file path
    @param content_type: The content type
    @return:
    """
    file_name = file_path.name
    query = select(MultimodalPartDBModel).filter(MultimodalPartDBModel.name == file_name)
    result = await session.execute(query)
    part = result.scalars().first()
    if part is None:
        logger.error("No database entry found for the file.")
        return

    try:
        if content_type in ["image", "video"]:
            thumbnail_func = create_image_thumbnail if content_type == "image" else create_video_thumbnail
            thumbnail_img = thumbnail_func(file_path, THUMBNAIL_SIZE)
            if thumbnail_img:
                files_dir = Path(os.environ["FILES_DIR"])
                thumbnail_path = files_dir / f"thumbnail_{file_path.stem}.jpg"
                thumbnail_img.save(thumbnail_path)

        multimodal_part = MultimodalPartFactory.from_path(file_path)
        multimodal_part.clear_cache()
        await run_in_threadpool(multimodal_part.upload)
        logger.info(f"Uploaded file {file_path}")
        part.status = EntryStatus.READY
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        part.status = EntryStatus.ERROR
        error_message = getattr(e, 'reason', getattr(e, 'message', str(e)))
        part.status_message = error_message
    finally:
        await session.commit()


@api.post("/uploadFile")
async def upload_file_handler(request: Request, background_tasks: BackgroundTasks,
                              upload_file: UploadFile = File(alias="file"),
                              db_session: AsyncSession = Depends(get_db_session)
                              ):
    """
    Hello endpoint
    :return:
    """
    try:
        mime_type = upload_file.content_type
        supported_content_types = ["image/png", "image/jpeg", "image/jpg", "video/mp4", "audio/mpeg", "audio/mp3"]
        if mime_type not in supported_content_types:
            return JSONResponse(content={"error": f"Unsupported content type: {mime_type}"})
        content_type = {
            "image/png": "image",
            "image/jpeg": "image",
            "image/jpg": "image",
            "video/mp4": "video",
            "audio/mpeg": "audio",
            "audio/mp3": "audio"
        }[mime_type]

        file_name = upload_file.filename
        cache_folder = get_gemini_playground_cache_dir()

        file_path = Path(cache_folder).joinpath(file_name)
        with open(file_path, "wb") as file:
            file_bytes = await upload_file.read()
            file.write(file_bytes)
        new_part = MultimodalPartDBModel(
            name=file_name,
            content_type=content_type
        )
        db_session.add(new_part)
        await db_session.commit()
        background_tasks.add_task(upload_file_task, file_path, content_type)
        return JSONResponse(content={"content": "File uploaded"})
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=repr(e))


async def delete_multimodal_part_files(multimodal_part):
    """
    Delete remote files
    """
    try:
        await run_in_threadpool(lambda: multimodal_part.delete())
    except Exception as e:
        logger.error(e)


@api.delete("/parts/{part_id}")
async def delete_part_handler(request: Request, background_tasks: BackgroundTasks, part_id: str,
                              db_session: AsyncSession = Depends(get_db_session)):
    """
    Delete part
    :return:
    """
    try:
        public_files_dir = Path(os.environ["FILES_DIR"])
        cache_folder = get_gemini_playground_cache_dir()
        repo_folder = cache_folder.joinpath("repos")
        logger.info(f"Deleting part {part_id}")
        query = select(MultimodalPartDBModel).filter(MultimodalPartDBModel.name == part_id)
        result = await db_session.execute(query)
        multimodal_part_db_entry = result.scalars().first()
        if multimodal_part_db_entry:
            if multimodal_part_db_entry.content_type == "repo":
                repo_folder = repo_folder.joinpath(part_id)
                if repo_folder.exists():
                    shutil.rmtree(repo_folder)
            else:
                multimodal_part = MultimodalPartFactory.from_path(cache_folder.joinpath(part_id))
                background_tasks.add_task(delete_multimodal_part_files, multimodal_part)
                file = cache_folder.joinpath(part_id)
                if file.exists():
                    file.unlink()
                thumbnail_file = public_files_dir.joinpath(f"thumbnail_{Path(part_id).stem}.jpg")
                if thumbnail_file.exists():
                    thumbnail_file.unlink()
            await db_session.delete(multimodal_part_db_entry)
            await db_session.commit()
        return JSONResponse(content={"content": "Part deleted"})
    except HttpError as e:
        logger.error(e)
        raise HTTPException(status_code=e.status_code, detail=e.reason)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=repr(e))
