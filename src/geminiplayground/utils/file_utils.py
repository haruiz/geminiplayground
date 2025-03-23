import os
import ssl
import shutil
import tempfile
import urllib.request
from pathlib import Path
from typing import Any, Generator, ContextManager, Union
from contextlib import contextmanager
from urllib.error import HTTPError
from urllib.parse import urlparse

import validators

# Disable SSL verification globally (not ideal in production)
ssl._create_default_https_context = ssl._create_unverified_context


class FileUtils:
    """
    A utility class for file and URL handling operations,
    including temporary file management, URL downloads,
    and size formatting.
    """

    @classmethod
    def clear_folder(cls, path: Path | str) -> None:
        """
        Recursively remove a directory and all its contents.

        Args:
            path: Directory path to clear.
        """
        path = Path(path)
        if not path.exists():
            return
        for child in path.glob("*"):
            if child.is_file():
                child.unlink()
            else:
                shutil.rmtree(child, ignore_errors=True)

    @classmethod
    @contextmanager
    def temporary_directory(cls, **kwargs) -> Generator[str, None, None]:
        """
        Create a temporary directory that is automatically cleaned up.

        Yields:
            Path to the temporary directory as a string.
        """
        dir_path = tempfile.mkdtemp(**kwargs)
        try:
            yield dir_path
        finally:
            cls.clear_folder(dir_path)
            if os.path.exists(dir_path):
                os.rmdir(dir_path)

    @staticmethod
    @contextmanager
    def temporary_file(**kwargs) -> Generator[tempfile.NamedTemporaryFile, None, None]:
        """
        Create a temporary file that is deleted on exit.

        Yields:
            A file-like object.
        """
        tmp = tempfile.NamedTemporaryFile(delete=False, **kwargs)
        try:
            yield tmp
        finally:
            tmp.close()
            os.unlink(tmp.name)

    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Convert gs:// links to https URLs, and validate others.

        Args:
            url: The input URI.

        Returns:
            A valid HTTP(S) URL.

        Raises:
            Exception: If scheme is unsupported.
        """
        parts = urlparse(url)
        if parts.scheme == "gs":
            return "https://storage.googleapis.com/" + url.replace("gs://", "").replace(" ", "%20")
        elif parts.scheme in ["http", "https"]:
            return url
        raise ValueError(f"Unsupported URL scheme: {parts.scheme}")

    @classmethod
    @contextmanager
    def get_path_from_url(cls, url: str) -> Generator[str, None, None]:
        """
        Download a file from a URL to a temporary file.

        Args:
            url: URL to the file.

        Yields:
            Path to the downloaded file.

        Raises:
            Exception: For unreachable or invalid URLs.
        """
        http_url = cls.normalize_url(url)
        if not validators.url(http_url):
            raise ValueError("Invalid URL")

        try:
            response = urllib.request.urlopen(http_url, timeout=30)
            filename = cls.get_file_name_from_path(url)
            stem, ext = Path(filename).stem, Path(filename).suffix

            with cls.temporary_file(prefix=stem, suffix=ext) as temp_file:
                with open(temp_file.name, "wb") as f:
                    f.write(response.read())
                yield temp_file.name

        except HTTPError as e:
            if e.code == 404:
                raise FileNotFoundError("File not found (404).")
            elif e.code in (403, 406):
                raise PermissionError("Access to the file is forbidden.")
            raise

    @staticmethod
    @contextmanager
    def get_path_from_local(path: Path | str) -> Generator[str, Any, None]:
        """
        Return a local file path in a context manager.

        Args:
            path: Local file path.

        Yields:
            The path itself.
        """
        yield str(path)

    @classmethod
    def solve_file_path(cls, path_or_uri: Path | str) -> ContextManager[str]:
        """
        Resolves either a local path or a remote URL to a context manager.

        Args:
            path_or_uri: Local path or remote URI.

        Returns:
            A context manager yielding the usable file path.
        """
        path_or_uri = str(path_or_uri)
        return cls.get_path_from_url(path_or_uri) if validators.url(path_or_uri) else cls.get_path_from_local(
            path_or_uri)

    @staticmethod
    def get_file_name_from_path(path: Path | str, include_extension: bool = True) -> str:
        """
        Extract the filename from a given path or URL.

        Args:
            path: The full path or URI.
            include_extension: Whether to include file extension.

        Returns:
            The file name with or without extension.
        """
        path = Path(urlparse(path).path if validators.url(str(path)) else path)
        return path.name if include_extension else path.stem

    @staticmethod
    def get_file_size(file_path: Path | str) -> int:
        """
        Get size of file in bytes.

        Args:
            file_path: Path to file.

        Returns:
            File size in bytes.
        """
        return os.path.getsize(file_path)

    @staticmethod
    def humanize_file_size(size_in_bytes: float) -> str:
        """
        Converts bytes to human-readable format.

        Args:
            size_in_bytes: Raw byte size.

        Returns:
            Readable file size string (e.g., 1.23 MB).
        """
        units = ["Bytes", "KB", "MB", "GB", "TB", "PB"]
        size = size_in_bytes
        unit_index = 0

        while size > 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1

        return f"{size:.2f} {units[unit_index]}"
