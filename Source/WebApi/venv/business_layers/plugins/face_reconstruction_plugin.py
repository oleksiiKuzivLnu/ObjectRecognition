from typing import List
import base64
import cv2

from .image_processor_plugin import ImageProcessorPlugin
from ...domains.models.image_artifact import ImageArtifact
from .reconstruction.demo import demo


class FaceReconstructionPlugin(ImageProcessorPlugin):
    def process(self, input: List[ImageArtifact]) -> str:
        _, buffer = cv2.imencode('.jpg', input[0].data)

        # Convert the byte stream to a base64 string
        base64_string = base64.b64encode(buffer).decode('utf-8')
        res = demo(base64_string)
        return res
