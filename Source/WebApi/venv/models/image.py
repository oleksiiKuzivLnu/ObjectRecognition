import base64

from ..domains.models.media_file import MediaFile


class Image:
    def __init__(self, file: MediaFile):
        self._file = file

    def to_dict(self):
        img_base64 = base64.b64encode(self._file.data)
        img_base64_string = img_base64.decode("utf-8")
        return f"data:{self._file.mediaType};base64," + img_base64_string
