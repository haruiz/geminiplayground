from geminiplayground.parts import MultimodalPartFactory, GitRepo
from geminiplayground.schemas import TextPart
from geminiplayground.utils import split_and_label_prompt_parts_from_string, get_gemini_playground_cache_dir
from geminiplayground.web.db.models import MultimodalPartEntry
from geminiplayground.web.db.orm_session import SessionMaker


def get_parts_from_prompt_text(prompt):
    """
    transform prompt into parts
    :param prompt:
    :return:
    """
    prompt_parts = split_and_label_prompt_parts_from_string(prompt)
    cache_dir = get_gemini_playground_cache_dir()
    files_dir = cache_dir
    repos_dir = cache_dir.joinpath("repos")
    parts = []
    for part in prompt_parts:
        if part["type"] == "text":
            parts.append(TextPart(text=part["value"]))
        elif part["type"] == "multimodal":
            session = SessionMaker()
            part_entry = session.query(MultimodalPartEntry).filter(MultimodalPartEntry.name == part["value"]).first()
            if part_entry:
                is_image = part_entry.content_type == "image"
                is_video = part_entry.content_type == "video"
                is_repo = part_entry.content_type == "repo"
                if any([is_image, is_video]):
                    file_path = files_dir.joinpath(part_entry.name)
                    multimodal_part = MultimodalPartFactory.from_path(file_path)
                    parts.extend(multimodal_part.content_parts())
                elif is_repo:
                    repo_folder = repos_dir.joinpath(part_entry.name)
                    repo = GitRepo.from_folder(repo_folder, config={
                        "content": "code-files",  # "code-files" or "issues"
                        "file_extensions": [".py"],
                    })
                    parts.extend(repo.content_parts())
                else:
                    raise Exception(f"Unsupported content type: {part_entry.content_type}")
    return parts
