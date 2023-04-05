from abc import ABC, abstractmethod
from ..plugins.image_processor_plugin import ImageProcessorPlugin


class ImageProcessorPluginAbstractFactory(ABC):
    @abstractmethod
    def createPlugin(self, pluginIdentifier: str) -> ImageProcessorPlugin:
        pass