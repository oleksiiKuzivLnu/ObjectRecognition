from typing import Dict


class ImageArtifact:
    def __init__(self, data: bytes, metadata: Dict[str, object]):
        self._data = data
        self._metadata = metadata