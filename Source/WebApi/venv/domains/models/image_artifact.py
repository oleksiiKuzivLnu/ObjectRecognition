from typing import Dict

import numpy as np


class ImageArtifact:
    def __init__(self, data: np.ndarray, metadata: Dict[str, object]):
        self._data = data
        self._metadata = metadata

    @property
    def data(self) -> np.ndarray:
        return self._data

    @property
    def metadata(self) -> Dict[str, object]:
        return self._metadata
