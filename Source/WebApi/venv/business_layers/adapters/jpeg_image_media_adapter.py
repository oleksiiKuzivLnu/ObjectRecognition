from typing import List, Dict
from .abstract_media_adapter import AbstractMediaAdapter
from ...domains.models.media_file import MediaFile
from ...domains.models.image_artifact import ImageArtifact


class JpegImageMediaAdapter(AbstractMediaAdapter):
    def toImageArtifacts(self, mediaFile: MediaFile) -> List[ImageArtifact]:
        # jpeg image adapter logic
        pass