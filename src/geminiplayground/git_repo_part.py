import logging
import typing
from pathlib import Path
from urllib.parse import urlparse

import git
from alive_progress import alive_bar
from github import Github

from geminiplayground import GeminiClient, TextPart
from geminiplayground.multi_modal_part import MultimodalPart
from geminiplayground.utils import get_playground_cache_dir, get_code_files_in_dir

logger = logging.getLogger("rich")


class GitRemoteProgress(git.RemoteProgress):
    OP_CODES = [
        "BEGIN",
        "CHECKING_OUT",
        "COMPRESSING",
        "COUNTING",
        "END",
        "FINDING_SOURCES",
        "RECEIVING",
        "RESOLVING",
        "WRITING",
    ]
    OP_CODE_MAP = {
        getattr(git.RemoteProgress, _op_code): _op_code for _op_code in OP_CODES
    }

    def __init__(self) -> None:
        super().__init__()
        self.alive_bar_instance = None

    @classmethod
    def get_curr_op(cls, op_code: int) -> str:
        """Get OP name from OP code."""
        # Remove BEGIN- and END-flag and get op name
        op_code_masked = op_code & cls.OP_MASK
        return cls.OP_CODE_MAP.get(op_code_masked, "?").title()

    def update(
            self,
            op_code: int,
            cur_count,
            max_count=None,
            message="",
    ) -> None:
        # Start new bar on each BEGIN-flag
        if op_code & self.BEGIN:
            self.curr_op = self.get_curr_op(op_code)
            self._dispatch_bar(title=self.curr_op)

        self.bar(cur_count / max_count)
        self.bar.text(message)

        # End progress monitoring on each END-flag
        if op_code & git.RemoteProgress.END:
            self._destroy_bar()

    def _dispatch_bar(self, title="") -> None:
        """Create a new progress bar"""
        self.alive_bar_instance = alive_bar(manual=True, title=title)
        self.bar = self.alive_bar_instance.__enter__()

    def _destroy_bar(self) -> None:
        """Destroy an existing progress bar"""
        self.alive_bar_instance.__exit__(None, None, None)


def folder_contains_git_repo(path):
    """
    Check if a given folder is a git repository
    :param path:
    :return: True if the given folder is a repor or false otherwise
    """
    try:
        _ = git.Repo(path).git_dir
        return True
    except (git.exc.InvalidGitRepositoryError, Exception):
        return False


def get_repo_name_from_url(url: str) -> str:
    """
    Get and return the repo name from a valid github url
    :rtype: str
    """
    last_slash_index = url.rfind("/")
    last_suffix_index = url.rfind(".git")
    if last_suffix_index < 0:
        last_suffix_index = len(url)
    if last_slash_index < 0 or last_suffix_index <= last_slash_index:
        raise Exception("invalid url format {}".format(url))
    return url[last_slash_index + 1: last_suffix_index]


class GitRepo(MultimodalPart):
    def __init__(self, repo_folder: typing.Union[str, Path], **kwargs):
        # set the output directory for the repos
        try:
            repo_folder = Path(repo_folder).resolve(strict=True)
            logger.info(f"Checking if {repo_folder} is a git repository")

            assert repo_folder.exists(), f"{repo_folder} does not exist"
            assert folder_contains_git_repo(repo_folder), f"{repo_folder} is not a git repository"

            self.repo_folder = repo_folder
            self.repo = git.Repo(repo_folder)
            self.gemini_client = kwargs.get("gemini_client", GeminiClient())

            self.config = kwargs.setdefault("config", {"content": "code-files"})
            self.content = self.config.get("content", "code-files")

            logger.info(f"Repo folder: {self.repo_folder}")
            logger.info(f"Content: {self.content}")
            logger.info(f"Config: {self.config}")

            valid_contents = {"code-files", "issues"}
            if self.content not in valid_contents:
                raise ValueError(f"Invalid content {self.content}, should be code-files or issues")
        except Exception as e:
            logger.error(e)
            raise e

    @classmethod
    def from_folder(cls, folder: str, **kwargs):
        """
        Create a GitRepo instance from a folder
        :param folder: the folder to create the GitRepo instance from
        :param kwargs: additional arguments to pass to the GitRepo constructor
        :return:
        """

        return cls(folder, **kwargs)

    @classmethod
    def from_repo_url(cls, repo_url: str, branch: str = "main", **kwargs):
        """
        Create a GitRepo instance from a repo url
        :param repo_url: the url of the repo to create the GitRepo instance from
        :param branch: the branch to clone the repo from
        :param kwargs: additional arguments to pass to the GitRepo constructor
        :return:
        """
        playground_cache_dir = get_playground_cache_dir()
        default_repos_folder = playground_cache_dir.joinpath("repos")
        repos_folder = kwargs.get("repos_folder", default_repos_folder)
        repos_folder = Path(repos_folder)
        repos_folder.mkdir(parents=True, exist_ok=True)

        repo_name = get_repo_name_from_url(repo_url)
        repo_folder = repos_folder.joinpath(repo_name)
        repo_folder.mkdir(parents=True, exist_ok=True)

        folder_is_empty = not any(repo_folder.iterdir())
        if folder_is_empty:
            try:
                git.Repo.clone_from(
                    url=repo_url,
                    to_path=repo_folder,
                    branch=branch,
                    progress=GitRemoteProgress(),
                )
            except Exception as e:
                logger.error(e)
                raise e
        config = kwargs.setdefault("config", {"content": "code-files"})
        print(repo_folder, config)
        return cls(repo_folder, config=config)

    def __get_parts_from_code_files(self):
        """
        Get the code parts from the repo
        :return:
        """
        file_extensions = self.config.get("file_extensions", None)
        exclude_dirs = self.config.get("exclude_dirs", None)

        code_files = get_code_files_in_dir(self.repo_folder, file_extensions, exclude_dirs)
        parts = []
        for file in code_files:
            with open(file, "r") as f:
                code_content = f.read()
                parts.append(TextPart(text="\n" + "file: " + file.name + "\n"))
                parts.append(TextPart(text=code_content))
        return parts

    def __get_parts_from_repos_issues(self):
        """
        Get the issues from the repo
        :return:
        """
        issues_state = self.config.get("issues_state", "open")

        remotes = self.repo.remotes
        assert len(remotes) > 0, "No remotes found"
        remote = remotes[0]
        url = remote.url
        g = Github()
        repo_path = urlparse(url).path[1:]
        remote_repo = g.get_repo(repo_path)
        issues = remote_repo.get_issues(state=issues_state)
        parts = []
        for issue in issues:
            parts.append(TextPart(text=issue.title))
        return parts

    def content_parts(self):
        """
        Get the content parts for the repo
        :param category: the category of the content parts to get
        :return:
        """
        try:
            functions_map = {
                "code-files": self.__get_parts_from_code_files,
                "issues": self.__get_parts_from_repos_issues
            }
            return functions_map[self.content]()
        except Exception as e:
            logger.error(e)
            raise e
