class MediaFile:
    def __init__(self, data: bytes, mediaType: str):
        self._data = data
        self._mediaType = mediaType

    @property
    def data(self) -> bytes:
        return self._data

    @property
    def mediaType(self) -> str:
        return self._mediaType
