import json
import base64

class Image:
    def __init__(self, data):
        self.data = data
    def to_dict(self):
        img_base64 = base64.b64encode(self.data)
        img_base64_string = img_base64.decode("utf-8")
        return {
            "return": json.dumps({"image": img_base64_string})
        }
