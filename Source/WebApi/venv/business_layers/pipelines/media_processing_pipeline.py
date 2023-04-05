from typing import List
from ..factories.image_processor_plugin_abstract_factory import ImageProcessorPluginAbstractFactory
from ..factories.abstract_media_adapter_factory import AbstractMediaAdapterFactory
from ...domains.models.media_file import MediaFile
from ...domains.models.image_artifact import ImageArtifact


class MediaProcessingPipeline:
    def __init__(self, pluginFactory: ImageProcessorPluginAbstractFactory, mediaAdapterFactory: AbstractMediaAdapterFactory, imageProcessorPluginIds: List[str], mediaFile: MediaFile):
        self._pluginFactory = pluginFactory
        self._mediaAdapterFactory = mediaAdapterFactory
        self._imageProcessorPluginIds = imageProcessorPluginIds
        self._mediaFile = mediaFile

    def process(self) -> List[ImageArtifact]:
        # media processing pipeline logic
        pass