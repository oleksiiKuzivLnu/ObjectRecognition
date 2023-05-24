from typing import List

import numpy as np
import cv2

from .abstract_media_adapter import AbstractMediaAdapter
from ...domains.models.media_file import MediaFile
from ...domains.models.image_artifact import ImageArtifact


class JpegImageMediaAdapter(AbstractMediaAdapter):
    def toImageArtifacts(self, mediaFile: MediaFile) -> List[ImageArtifact]:
        # TODO: Review as it is temporary
        buf = bytearray(mediaFile.data)
        bytes_buf = bytes(buf)

        img_np = np.frombuffer(bytes_buf, dtype=np.uint8)
        img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

        return [ImageArtifact(img, {})]

    def fromImageArtifacts(self, imageArtifacts: str | List[ImageArtifact]) -> bytes:
        if (type(imageArtifacts) is str): # face reconstruction
            return bytes(imageArtifacts, 'UTF-8')
        
        assert len(imageArtifacts) == 1

        img = imageArtifacts[0].data
        _, img_bytearray = cv2.imencode('.jpg', img)

        return img_bytearray
