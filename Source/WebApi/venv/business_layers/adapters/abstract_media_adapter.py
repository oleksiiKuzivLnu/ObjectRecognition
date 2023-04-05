from abc import ABC, abstractmethod
from typing import List
from domains.models.media_file import MediaFile
from domains.models.image_artifact import ImageArtifact


class AbstractMediaAdapter(ABC):
    @abstractmethod
    def toImageArtifacts(self, mediaFile: MediaFile) -> List[ImageArtifact]:
        pass