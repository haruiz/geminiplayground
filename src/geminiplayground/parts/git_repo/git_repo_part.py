import codecs
import logging
from pathlib import Path
from urllib.parse import urlparse

import git
from github import Github
from langchain_core.documents import Document

from geminiplayground.core import GeminiClient
from geminiplayground.utils import GitUtils, GitRemoteProgress, LibUtils
from ..multimodal_part import MultimodalPart

logger = logging.getLogger("rich")


class GitRepoBranchNotFoundException(Exception):
    """Exception raised when a branch does not exist in the remote repo."""


class GitRepo(MultimodalPart):
    """
    A multimodal part that represents a Git repository.

    Can extract either code files or GitHub issues depending on configuration.
    """

    def __init__(
            self,
            repo_folder: str | Path,
            gemini_client: GeminiClient = None,
            **kwargs,
    ):
        super().__init__(gemini_client)
        self._repo_folder = GitUtils.validate_repo_folder(repo_folder)
        self._repo = git.Repo(self._repo_folder)
        self._search_settings = kwargs.get("config", {"content": "code-files"})
        self._search_content_type = self._search_settings["content"]

        if self._search_content_type not in {"code-files", "issues"}:
            raise ValueError(
                f"Invalid content type: '{self._search_content_type}'. "
                "Supported types: 'code-files', 'issues'."
            )

        logger.info(f"Repo folder: {self._repo_folder}")
        logger.info(f"Content type: {self._search_content_type}")

    @classmethod
    def from_folder(cls, folder: str | Path, **kwargs):
        """
        Initialize GitRepo from a local repo folder.

        Args:
            folder: Path to local git repo.

        Returns:
            GitRepo instance.
        """
        return cls(folder, **kwargs)

    @classmethod
    def from_url(cls, repo_url: str, branch: str = "main", **kwargs):
        """
        Clone a Git repo from a remote URL and return a GitRepo instance.

        Args:
            repo_url: GitHub repo URL.
            branch: Branch name to clone.
            kwargs: Optional config and custom repo path.

        Returns:
            GitRepo instance.

        Raises:
            GitRepoBranchNotFoundException: If the branch doesn't exist.
        """
        repos_folder = Path(kwargs.get("repos_folder", LibUtils.get_lib_home() / "repos"))
        repos_folder.mkdir(parents=True, exist_ok=True)

        repo_name = GitUtils.get_repo_name_from_url(repo_url)
        repo_folder = repos_folder / repo_name
        repo_folder.mkdir(parents=True, exist_ok=True)

        if not GitUtils.check_github_repo_branch_exists(repo_url, branch):
            branches = GitUtils.get_github_repo_available_branches(repo_url)
            msg = f"Branch '{branch}' not found. Available: {branches}"
            logger.error(msg)
            raise GitRepoBranchNotFoundException(msg)

        if not any(repo_folder.iterdir()):  # only clone if folder is empty
            try:
                git.Repo.clone_from(
                    url=repo_url,
                    to_path=repo_folder,
                    branch=branch,
                    progress=GitRemoteProgress(),
                )
            except Exception as e:
                logger.exception("Failed to clone repository.")
                raise e

        config = kwargs.setdefault("config", {"content": "code-files"})
        return cls(repo_folder, config=config)

    def _get_parts_from_code_files(self) -> list[Document]:
        """
        Extract code content as LangChain Documents.

        Returns:
            List of Document objects containing file content and metadata.
        """
        extensions = self._search_settings.get("file_extensions")
        excludes = self._search_settings.get("exclude_dirs")
        files = GitUtils.get_code_files_in_dir(self._repo_folder, extensions, excludes)

        parts = []
        for file in files:
            try:
                with codecs.open(file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    parts.append(Document(
                        page_content=f"""file: {file}\n```python\n{content}\n```""",
                        metadata={"file_path": str(file), "category": "Code"},
                    ))
            except Exception as e:
                logger.warning(f"Failed to read {file}: {e}")

        return parts

    def _get_parts_from_repo_issues(self) -> list[Document]:
        """
        Retrieve GitHub issues from the remote repo.

        Returns:
            List of Document objects with issue title and body.

        Raises:
            AssertionError: If no remotes are found in local repo.
        """
        issues_state = self._search_settings.get("issues_state", "open")
        remotes = self._repo.remotes

        assert remotes, "No remote found in the repository."

        try:
            remote_url = remotes[0].url
            repo_path = urlparse(remote_url).path.lstrip("/")
            github = Github()
            repo = github.get_repo(repo_path)
            issues = repo.get_issues(state=issues_state)

            return [
                Document(
                    page_content=f"issue: {issue.title}\n\n{issue.body}",
                    metadata={"issue": issue.title, "category": "Issue"},
                )
                for issue in issues
            ]
        except Exception as e:
            logger.exception("Failed to retrieve GitHub issues.")
            return []

    def content_parts(self) -> list[Document]:
        """
        Get extracted content from the repository (code or issues).

        Returns:
            A list of Document objects.
        """
        content_func_map = {
            "code-files": self._get_parts_from_code_files,
            "issues": self._get_parts_from_repo_issues,
        }

        return content_func_map[self._search_content_type]()
