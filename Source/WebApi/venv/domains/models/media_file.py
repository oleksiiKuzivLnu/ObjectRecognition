class MediaFile:
    def __init__(self, data: bytes, mediaType: str):
        self._data = data
        self._mediaType = mediaType