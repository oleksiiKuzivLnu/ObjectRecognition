from .image_processor_plugin_abstract_factory import ImageProcessorPluginAbstractFactory
from ..plugins.image_processor_plugin import ImageProcessorPlugin
from ..plugins.face_reconstruction_plugin import FaceReconstructionPlugin

class ImageReconstructionPluginConcreteFactory(ImageProcessorPluginAbstractFactory):
    def createPlugin(self, pluginIdentifier: str) -> ImageProcessorPlugin:
        if pluginIdentifier == 'face_reconstruction':
            return FaceReconstructionPlugin()