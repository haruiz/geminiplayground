import math
from pathlib import Path

import cv2
from tqdm import tqdm

from geminiplayground.gemini_client import GeminiClient
from geminiplayground.multi_modal_part import MultimodalPart
from geminiplayground.utils import rm_tree, UploadFile, get_playground_cache_dir


class VideoFile(MultimodalPart):
    """
    Extract frames from a video and upload them to Gemini
    """

    def __init__(self, video_path: str, **kwargs):

        # Set the output directory for the frames
        default_videos_folder = get_playground_cache_dir().joinpath("videos")
        videos_folder = kwargs.get("videos_folder", default_videos_folder)

        self.video_path = Path(video_path)
        self.video_dir = videos_folder.joinpath(self.video_path.stem)
        self.video_dir.mkdir(parents=True, exist_ok=True)

        self.gemini_client = kwargs.get("gemini_client", GeminiClient())

    def extract_frames(self):
        """
        Extract frames from the video
        :return:
        """
        rm_tree(self.video_dir)
        self.video_dir.mkdir(parents=True, exist_ok=True)

        vidcap = cv2.VideoCapture(self.video_path.as_posix())
        fps = int(vidcap.get(cv2.CAP_PROP_FPS))
        duration = vidcap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
        num_frames = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
        print(f"Video duration: {duration} seconds")
        print(f"Total number of frames: {num_frames}")
        frame_file_prefix = self.video_path.stem

        frame_count = 0  # Initialize a frame counter
        count = 0
        with tqdm(
                total=math.ceil(duration), unit="sec", desc="Extracting frames"
        ) as pbar:
            while True:
                ret, frame = vidcap.read()
                if not ret:
                    break
                if count % int(fps) == 0:  # Extract a frame every second
                    frame_count += 1
                    frame_image_filename = (
                        f"{frame_file_prefix}_frame_{frame_count:04d}.jpg"
                    )
                    frame_image_path = self.video_dir.joinpath(
                        frame_image_filename
                    )
                    cv2.imwrite(frame_image_path.as_posix(), frame)
                    pbar.update(1)
                count += 1
        vidcap.release()

    def upload_frames(self):
        """
        Upload frames to Gemini
        :return:
        """
        # Process each frame in the output directory
        files = self.video_dir.glob("*.jpg")
        files = sorted(files)  # Sort alphabetically
        files_to_upload = []
        for file in files:
            # extract timestamp from filename
            timestamp_seconds = int(file.stem.split("_")[-1])
            files_to_upload.append(
                UploadFile(
                    file_path=file.as_posix(),
                    display_name=file.name,
                    timestamp_seconds=timestamp_seconds,
                )
            )

        # Upload files to Gemini
        for file in tqdm(files_to_upload, desc="Uploading frames to Gemini"):
            self.gemini_client.upload_file(
                file
            )

    def upload(self):
        """
        Start the upload process
        :return:
        """
        self.extract_frames()
        self.upload_frames()

    def content_parts(self):
        """
        Get the content parts for the video
        :return:
        """
        video_parts = self.gemini_client.get_file_parts(display_name_prefix=Path(self.video_path).stem)
        return video_parts
