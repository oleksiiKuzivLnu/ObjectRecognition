from abc import ABC, abstractmethod
from typing import List
from venv.domains.models.media_file import MediaFile
from venv.domains.models.image_artifact import ImageArtifact


class AbstractMediaAdapter(ABC):
    @abstractmethod
    def toImageArtifacts(self, mediaFile: MediaFile) -> List[ImageArtifact]:
        pass
