

class InputMediaProcessResponse:
    def __init__(self, images):
        self.images = images
    def to_dict(self):
        return {
            "images": self.images
        }
