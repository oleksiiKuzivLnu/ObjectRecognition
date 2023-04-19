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
        # create list of ImageProcessorPlugin objects
        plugins = [self._pluginFactory.createPlugin(pluginId) for pluginId in self._imageProcessorPluginIds]

        # get the ImageArtifacts from the media file using the media adapter factory
        mediaAdapter = self._mediaAdapterFactory.createAdapter(self._mediaFile._mediaType)
        imageArtifacts = mediaAdapter.toImageArtifacts(self._mediaFile)

        # call each plugin in the specified order to process the input
        for plugin in plugins:
            imageArtifacts = plugin.process(imageArtifacts)
        
        # return the final output
        return imageArtifacts