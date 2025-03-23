from io import BytesIO
from pathlib import Path
from typing import Union, Optional

import cv2
import math
from PIL import Image as PILImage
from PIL.Image import Image as PILImageType
from tqdm import tqdm
import random


class VideoUtils:
    """
    Utility class for performing various video operations,
    such as frame extraction, duration calculation, and thumbnail generation.
    """

    @staticmethod
    def extract_video_frames(
            video_path: Union[str, Path],
            output_dir: Union[str, Path]
    ) -> list[Path]:
        """
        Extract one frame per second from a video and save them to a directory.

        Args:
            video_path: Path to the video file.
            output_dir: Path to the directory to save extracted frames.

        Returns:
            A list of Paths to the saved frame images.
        """
        video_path = Path(video_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        vidcap = cv2.VideoCapture(str(video_path))
        fps = int(vidcap.get(cv2.CAP_PROP_FPS))
        frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps else 0

        saved_frames = []
        frame_index = 0
        video_name = video_path.stem

        with tqdm(total=math.ceil(duration), unit="sec", desc="Extracting frames") as pbar:
            while True:
                success, frame = vidcap.read()
                if not success:
                    break
                if frame_index % fps == 0:
                    frame_number = frame_index // fps + 1
                    filename = f"{video_name}_frame{frame_number:04d}.jpg"
                    frame_path = output_dir / filename
                    cv2.imwrite(str(frame_path), frame)
                    saved_frames.append(frame_path)
                    pbar.update(1)
                frame_index += 1

        vidcap.release()
        return saved_frames

    @staticmethod
    def extract_video_frame_count(video_path: Union[str, Path]) -> int:
        """
        Get the total number of frames in a video.

        Args:
            video_path: Path to the video file.

        Returns:
            Total frame count.
        """
        vidcap = cv2.VideoCapture(str(video_path))
        frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
        vidcap.release()
        return frame_count

    @staticmethod
    def extract_video_duration(video_path: Union[str, Path]) -> int:
        """
        Get the duration of the video in seconds.

        Args:
            video_path: Path to the video file.

        Returns:
            Duration in seconds.
        """
        vidcap = cv2.VideoCapture(str(video_path))
        fps = vidcap.get(cv2.CAP_PROP_FPS)
        total_frames = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
        vidcap.release()
        return int(total_frames / fps) if fps else 0

    @staticmethod
    def extract_video_frame_at_t(
            video_path: Union[str, Path],
            timestamp_seconds: int
    ) -> PILImageType:
        """
        Extract a single frame at a given timestamp.

        Args:
            video_path: Path to the video file.
            timestamp_seconds: Time in seconds to extract frame from.

        Returns:
            A PIL Image of the frame.

        Raises:
            ValueError: If frame could not be read.
        """
        vidcap = cv2.VideoCapture(str(video_path))
        fps = vidcap.get(cv2.CAP_PROP_FPS)
        frame_num = int(fps * timestamp_seconds)

        vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        success, frame = vidcap.read()
        vidcap.release()

        if not success:
            raise ValueError(f"Could not extract frame at {timestamp_seconds}s")

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return PILImage.fromarray(frame_rgb)

    @classmethod
    def create_video_thumbnail(
            cls,
            video_path: Union[str, Path],
            thumbnail_size: tuple[int, int] = (128, 128),
            t: Optional[int] = None
    ) -> PILImageType:
        """
        Create a thumbnail image from a specific timestamp in the video.

        Args:
            video_path: Path to the video.
            thumbnail_size: Size of the resulting thumbnail.
            t: Timestamp in seconds to extract frame from.

        Returns:
            A PIL Image object (RGB) thumbnail.
        """
        video_duration = cls.extract_video_duration(video_path)
        if t is None:
            t = random.randint(0, video_duration)
        frame = cls.extract_video_frame_at_t(video_path, t)
        frame.thumbnail(thumbnail_size)
        frame = frame.convert("RGB")

        thumbnail_bytes = BytesIO()
        frame.save(thumbnail_bytes, format="JPEG")
        thumbnail_bytes.seek(0)
        return PILImage.open(thumbnail_bytes)

    @staticmethod
    def seconds_to_time_string(seconds: int) -> str:
        """
        Convert seconds to "MM:SS" format.

        Args:
            seconds: Time in seconds.

        Returns:
            Formatted string.
        """
        minutes, sec = divmod(seconds, 60)
        return f"{minutes:02d}:{sec:02d}"

    @staticmethod
    def get_frame_number_from_filename(filename: str, prefix: str) -> int | None:
        """
        Extract frame number from a file name of format: 'video_frame0005.jpg'.

        Args:
            filename: Full filename.
            prefix: Frame prefix (e.g., '_frame').

        Returns:
            Extracted frame number or None if malformed.
        """
        try:
            return int(filename.split(prefix)[1].split(".")[0])
        except (IndexError, ValueError):
            return None

    @staticmethod
    def get_output_prefix_from_filename(filename: str, prefix: str) -> str | None:
        """
        Extract the output file prefix from a frame filename.

        Args:
            filename: Full filename like 'video_frame0005.jpg'.
            prefix: Frame prefix (e.g., '_frame').

        Returns:
            Prefix string before the frame section, or None if malformed.
        """
        parts = filename.split(prefix)
        return parts[0] if len(parts) == 2 else None


if __name__ == '__main__':
    pdf_path = "./../../../data/BigBuckBunny_320x180.mp4"
    thumbnail = VideoUtils.create_video_thumbnail(pdf_path)
    thumbnail.show()
