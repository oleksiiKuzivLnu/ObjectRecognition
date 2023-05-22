from abc import ABC, abstractmethod
from typing import List
from ...domains.models.image_artifact import ImageArtifact


class ImageProcessorPlugin(ABC):
    @abstractmethod
    def process(self, input: List[ImageArtifact]) -> List[ImageArtifact] | str:
        pass