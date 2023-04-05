from .image_processor_plugin_abstract_factory import ImageProcessorPluginAbstractFactory
from ..plugins.image_processor_plugin import ImageProcessorPlugin
from ..plugins.face_recognition_plugin import FaceRecognitionPlugin

class ImageProcessorPluginConcreteFactory(ImageProcessorPluginAbstractFactory):
    def createPlugin(self, pluginIdentifier: str) -> ImageProcessorPlugin:
        if pluginIdentifier == 'face_recognition':
            return FaceRecognitionPlugin()