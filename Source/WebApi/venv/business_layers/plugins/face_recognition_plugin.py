from typing import List
from .image_processor_plugin import ImageProcessorPlugin
from ...domains.models.image_artifact import ImageArtifact
import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO('./best.pt')
class_name_dict = {0: 'face'}
threshold = 0.0001


class FaceRecognitionPlugin(ImageProcessorPlugin):
    def process(self, input: List[ImageArtifact]) -> List[ImageArtifact]:
        img_np = np.frombuffer(input[0]._data, dtype=np.uint8)
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
        res = ImageArtifact(img_bytearray)
        return [res]