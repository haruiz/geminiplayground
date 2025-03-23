import subprocess
from pathlib import Path
from typing import List, Optional, Union

import git
import validators


class GitUtils:
    """
    Utility class for interacting with Git repositories.
    """

    @staticmethod
    def get_code_files_in_dir(
            root_dir: Union[str, Path],
            file_extensions: Optional[List[str]] = None,
            exclude_dirs: Optional[List[str]] = None
    ) -> List[Path]:
        """
        Recursively list code files in a directory, excluding unwanted folders.

        Args:
            root_dir: The root directory to scan.
            file_extensions: List of extensions to include (default: common code files).
            exclude_dirs: List of directories to exclude.

        Returns:
            A list of matching Path objects.
        """
        default_excludes = {
            ".git", "node_modules", ".venv", "__pycache__", ".idea",
            ".vscode", "build", "dist", "target"
        }

        ignore_dirs = default_excludes.union(exclude_dirs or [])

        if file_extensions is None:
            file_extensions = [".py", ".java", ".cpp", ".h", ".c", ".go", ".js", ".html", ".css", ".sh"]

        code_files = []
        for path in Path(root_dir).rglob("*"):
            if path.is_file() and path.suffix in file_extensions:
                if not any(exclude in path.parts for exclude in ignore_dirs):
                    code_files.append(path)

        return code_files

    @staticmethod
    def folder_contains_git_repo(path: Union[str, Path]) -> bool:
        """
        Check whether a given path is a Git repository.

        Args:
            path: The directory path.

        Returns:
            True if it contains a Git repository, False otherwise.
        """
        try:
            path = Path(path)
            return path.exists() and git.Repo(path).git_dir is not None
        except git.exc.InvalidGitRepositoryError:
            return False

    @staticmethod
    def validate_repo_folder(repo_folder: Union[str, Path]) -> Path:
        """
        Validate that a given folder exists and contains a Git repository.

        Args:
            repo_folder: Path to validate.

        Returns:
            Resolved Path object.

        Raises:
            FileNotFoundError: If the path does not exist.
            ValueError: If the path is not a Git repo.
        """
        repo_path = Path(repo_folder).resolve(strict=True)

        if not GitUtils.folder_contains_git_repo(repo_path):
            raise ValueError(f"{repo_path} is not a Git repository.")

        return repo_path

    @staticmethod
    def get_repo_name_from_url(url: str) -> str:
        """
        Extract the repository name from a Git remote URL.

        Args:
            url: The Git URL (e.g., https://github.com/org/repo.git).

        Returns:
            The repository name (e.g., "repo").

        Raises:
            ValueError: If the URL format is invalid.
        """
        if not validators.url(url):
            raise ValueError(f"Invalid URL format: {url}")

        last_slash = url.rfind("/")
        suffix_index = url.rfind(".git")
        suffix_index = suffix_index if suffix_index != -1 else len(url)

        if last_slash < 0 or suffix_index <= last_slash:
            raise ValueError(f"Invalid GitHub URL: {url}")

        return url[last_slash + 1: suffix_index]

    @classmethod
    def get_repo_name_from_path(cls, path: Union[str, Path]) -> str:
        """
        Get the Git repo name from a local repo path.

        Args:
            path: Local path.

        Returns:
            The name of the repo directory.

        Raises:
            AssertionError: If the path is not a Git repo.
        """
        assert cls.folder_contains_git_repo(path), f"{path} is not a valid Git repository."
        return Path(path).name

    @classmethod
    def get_repo_name(cls, path_or_url: Union[str, Path]) -> str:
        """
        Get the Git repository name from a path or URL.

        Args:
            path_or_url: Either a local path or a remote URL.

        Returns:
            The repo name.
        """
        if validators.url(str(path_or_url)):
            return cls.get_repo_name_from_url(str(path_or_url))
        return cls.get_repo_name_from_path(path_or_url)

    @staticmethod
    def get_github_repo_available_branches(remote_url: str) -> List[str]:
        """
        List available branches in a remote GitHub repository.

        Args:
            remote_url: The GitHub repo URL.

        Returns:
            List of branch names.

        Raises:
            subprocess.CalledProcessError: If git ls-remote fails.
        """
        output = subprocess.check_output(["git", "ls-remote", "--heads", remote_url])
        lines = output.decode("utf-8").strip().split("\n")
        return [line.split("refs/heads/")[1] for line in lines if "refs/heads/" in line]

    @classmethod
    def check_github_repo_branch_exists(cls, remote_url: str, branch_name: str) -> bool:
        """
        Check if a specific branch exists in a GitHub repository.

        Args:
            remote_url: GitHub repository URL.
            branch_name: Branch to check.

        Returns:
            True if the branch exists, False otherwise.
        """
        branches = cls.get_github_repo_available_branches(remote_url)
        return branch_name in branches
