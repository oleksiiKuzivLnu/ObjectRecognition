from typing import List
from .image_processor_plugin import ImageProcessorPlugin
from ...domains.models.image_artifact import ImageArtifact


class FaceRecognitionPlugin(ImageProcessorPlugin):
    def process(self, input: List[ImageArtifact]) -> List[ImageArtifact]:
        # face recognition plugin logic
        pass