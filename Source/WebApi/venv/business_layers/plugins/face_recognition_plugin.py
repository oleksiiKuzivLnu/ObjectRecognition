from typing import List
from .image_processor_plugin import ImageProcessorPlugin
from ...domains.models.image_artifact import ImageArtifact
import cv2
import numpy as np
from ultralytics import YOLO
import os

model = YOLO(os.path.abspath(r"./venv/business_layers/plugins/best.pt"))
class_name_dict = {0: 'face'}
threshold = 0.0001


class FaceRecognitionPlugin(ImageProcessorPlugin):
    def process(self, input: List[ImageArtifact]) -> List[ImageArtifact]:
        with open('C:/1c698dd38f3d4aba.jpg', 'rb') as f:
            img_bytes = f.read()

        img_np = np.frombuffer(img_bytes, dtype=np.uint8) #input[0]._data
        photo = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        img = photo
        results= model(img)[0].boxes.data.tolist()
        for result in results:
            x1, y1, x2, y2, score, class_id = result
            if score > threshold:
                cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 4)
                cv2.putText(img, class_name_dict[int(class_id)].upper(), (int(x1), int(y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)

        _, img_bytearray = cv2.imencode('.jpg', img)
        res = ImageArtifact(img_bytearray, {})
        return [res]
