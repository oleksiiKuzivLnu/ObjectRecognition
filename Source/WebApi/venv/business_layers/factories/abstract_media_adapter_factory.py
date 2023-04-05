from abc import ABC,abstractmethod
from ..adapters.abstract_media_adapter import AbstractMediaAdapter


class AbstractMediaAdapterFactory(ABC):
    @abstractmethod
    def createAdapter(self, mediaType: str) -> 'AbstractMediaAdapter':
        pass