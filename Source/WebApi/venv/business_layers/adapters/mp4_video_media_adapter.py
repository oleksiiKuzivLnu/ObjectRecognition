from typing import List
import tempfile

import cv2

from .abstract_media_adapter import AbstractMediaAdapter
from ...domains.models.media_file import MediaFile
from ...domains.models.image_artifact import ImageArtifact


class Mp4VideoMediaAdapter(AbstractMediaAdapter):
    def toImageArtifacts(self, mediaFile: MediaFile) -> List[ImageArtifact]:
        buf = bytearray(mediaFile.data)
        bytes_buf = bytes(buf)

        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_video.write(bytes_buf)
        temp_video.close()
        video = cv2.VideoCapture(temp_video.name)

        image_artifacts = []

        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                break

            h, w, _ = frame.shape
            image_artifacts.append(ImageArtifact(frame, {'h': h, 'w': w, 'fps': int(video.get(cv2.CAP_PROP_FPS))}))

        video.release()

        return image_artifacts

    def fromImageArtifacts(self, imageArtifacts: List[ImageArtifact]) -> bytes:
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")

        meta = imageArtifacts[0].metadata
        h, w = meta['h'], meta['w']
        fps = meta['fps']

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_video.name, fourcc, fps, (w, h))

        for imageArtifact in imageArtifacts:
            frame = imageArtifact.data
            out.write(frame)

        out.release()

        video_bytes = temp_video.read()
        temp_video.close()
        return video_bytes
