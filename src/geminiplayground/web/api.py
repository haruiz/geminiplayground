import logging

from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from googleapiclient.errors import HttpError

from geminiplayground.core import GeminiClient
from geminiplayground.parts import MultimodalPartFactory, GitRepo, GitRepoBranchNotFoundException
from geminiplayground.schemas import CandidatesSchema, TextPart, GenerateRequest, \
    GenerateRequestParts, \
    GenerationSettings
from geminiplayground.utils import *
from .db.models import MultimodalPartEntry
from .db.orm_session import SessionMaker
from .utils import get_parts_from_prompt_text

logger = logging.getLogger("rich")

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
async def upload_file_handler(request: Request, upload_file: UploadFile = File(alias="file")):
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
    cache_folder = get_gemini_playground_cache_dir()

    file_path = Path(cache_folder).joinpath(file_name)
    with open(file_path, "wb") as file:
        file_bytes = await upload_file.read()
        file.write(file_bytes)

    multimodal_part = MultimodalPartFactory.from_path(file_path)
    multimodal_part.upload()

    if content_type == "image":
        thumbnail_img = create_image_thumbnail(file_path, THUMBNAIL_SIZE)
    elif content_type == "video":
        thumbnail_img = create_video_thumbnail(file_path, THUMBNAIL_SIZE)
    else:
        raise Exception(f"Unsupported content type: {content_type}")

    part_thumbnail_path = Path(public_files_dir).joinpath(f"thumbnail_{Path(file_name).stem}.jpg")
    thumbnail_img.save(part_thumbnail_path)

    session = SessionMaker()
    try:
        multimodal_part_db_entry = MultimodalPartEntry(
            name=file_name,
            content_type=content_type
        )
        session.add(multimodal_part_db_entry)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=repr(e))

    return JSONResponse(content={"content": "File uploaded"})


@api.post("/uploadRepo")
async def upload_repo_handler(request: Request):
    """
    Hello endpoint
    :return:
    """

    body_data = await request.json()
    repo_path = body_data.get("repoPath")
    repo_branch = body_data.get("repoBranch")
    session = SessionMaker()
    try:
        if validators.url(repo_path):
            repo = GitRepo.from_repo_url(repo_path, branch=repo_branch)
        else:
            repo = GitRepo.from_folder(repo_path)
        multimodal_part_db_entry = MultimodalPartEntry(
            name=repo.repo_folder.name,
            content_type="repo"
        )
        session.add(multimodal_part_db_entry)
        session.commit()
    except (GitRepoBranchNotFoundException, Exception) as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=repr(e))

    return JSONResponse(content={"content": "Repository created"})


@api.get("/parts")
def get_parts_handler():
    """
    Get parts
    :return:
    """
    session = SessionMaker()
    parts = session.query(MultimodalPartEntry).all()
    parts = [part.as_dict() for part in parts]
    return parts


@api.get("/models")
def get_models_handler():
    """
    Get models
    :return:
    """
    models = gemini_client.query_models()
    models = list(sorted(models, key=lambda model: model.input_token_limit, reverse=True))
    return models


@api.get("/tags")
def get_tags_handler(request: Request):
    """
    Get tags
    :return:
    """
    request_url = request.url._url
    base_url = request_url.split("/api")[0]
    files_url = f"{base_url}/files"
    session = SessionMaker()
    parts = session.query(MultimodalPartEntry).all()
    tags = []
    for part in parts:
        if part.content_type == "repo":
            thumbnail_url = f"{files_url}/thumbnail_github.png"
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


@api.delete("/parts/{part_id}")
def delete_part_handler(part_id: str):
    """
    Delete part
    :return:
    """
    session = SessionMaker()
    try:
        public_files_dir = Path(os.environ["FILES_DIR"])
        cache_folder = get_gemini_playground_cache_dir()
        repo_folder = cache_folder.joinpath("repos")

        multimodal_part_db_entry = session.query(MultimodalPartEntry).filter(
            MultimodalPartEntry.name == part_id).first()
        if multimodal_part_db_entry:
            if multimodal_part_db_entry.content_type == "repo":
                repo_folder = repo_folder.joinpath(part_id)
                if repo_folder.exists():
                    shutil.rmtree(repo_folder)
            else:
                multimodal_part = MultimodalPartFactory.from_path(cache_folder.joinpath(part_id))
                multimodal_part.delete()
                file = cache_folder.joinpath(part_id)
                if file.exists():
                    file.unlink()
                thumbnail_file = public_files_dir.joinpath(f"thumbnail_{Path(part_id).stem}.jpg")
                if thumbnail_file.exists():
                    thumbnail_file.unlink()
            session.delete(multimodal_part_db_entry)
            session.commit()
        return JSONResponse(content={"content": "Part deleted"})
    except HttpError as e:
        logger.error(e)
        session.rollback()
        raise HTTPException(status_code=e.status_code, detail=e.reason)
    # handle other exceptions
    except Exception as e:
        logger.error(e)
        session.rollback()
        raise HTTPException(status_code=500, detail=repr(e))


@api.post("/generate")
async def generate_handler(request: Request) -> CandidatesSchema:
    """
    Generate
    :return:
    """
    try:
        request_json = await request.json()
        prompt = request_json.get("message")
        generative_model = request_json.get("model")
        generate_settings = request_json.get("settings", None)
        prompt_parts = get_parts_from_prompt_text(prompt)
        prompt_request = GenerateRequest(
            contents=[
                GenerateRequestParts(parts=prompt_parts)
            ]
        )
        if generate_settings:
            prompt_request.generation_config = GenerationSettings.parse_obj(generate_settings)
        prompt_response = gemini_client.generate_response(generative_model, prompt_request)
        return prompt_response
    except HttpError as e:
        raise HTTPException(status_code=e.status_code, detail=e.reason)
    # handle other exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=repr(e))


async def gemini_response_generator(generative_model, prompt_request):
    candidates = gemini_client.generate_response(generative_model, prompt_request, stream=True, timeout=0.5)
    for candidate in candidates:
        yield candidate.text


@api.post("/generateStream")
async def generate_handler(request: Request) -> StreamingResponse:
    """
    Generate
    :return:
    """
    try:
        request_json = await request.json()
        prompt = request_json.get("message")
        generative_model = request_json.get("model")
        generate_settings = request_json.get("settings", None)

        prompt_request = GenerateRequest(
            contents=[
                GenerateRequestParts(parts=[
                    TextPart(text=prompt)
                ])
            ]
        )
        if generate_settings:
            prompt_request.generation_config = GenerationSettings.parse_obj(generate_settings)
        return StreamingResponse(gemini_response_generator(generative_model, prompt_request))
    except HttpError as e:
        print(e)
        raise HTTPException(status_code=e.status_code, detail=e.reason)
    # handle other exceptions
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=repr(e))
