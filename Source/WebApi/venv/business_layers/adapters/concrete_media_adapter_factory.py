from ..factories.abstract_media_adapter_factory import AbstractMediaAdapterFactory
from .jpeg_image_media_adapter import JpegImageMediaAdapter
from .abstract_media_adapter import AbstractMediaAdapter


class ConcreteMediaAdapterFactory(AbstractMediaAdapterFactory):
    def createAdapter(self, mediaType: str) -> 'AbstractMediaAdapter':
        if mediaType == 'JPEG':
            return JpegImageMediaAdapter()
        raise ValueError(f"Unsupported media type")