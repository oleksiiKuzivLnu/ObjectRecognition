from typing import List
import os

import cv2
from ultralytics import YOLO

from .image_processor_plugin import ImageProcessorPlugin
from ...domains.models.image_artifact import ImageArtifact


model = YOLO(os.path.abspath(r"./venv/business_layers/plugins/best.pt"))
class_name_dict = {0: 'face'}
threshold = 0.0001


class FaceRecognitionPlugin(ImageProcessorPlugin):
    def process(self, input: List[ImageArtifact]) -> List[ImageArtifact]:
        output = []

        for image_artifact in input:
            img = image_artifact.data
            results = model(img)[0].boxes.data.tolist()
            for result in results:
                x1, y1, x2, y2, score, class_id = result
                if score > threshold:
                    cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 4)

            output.append(ImageArtifact(img, image_artifact.metadata))

        return output
