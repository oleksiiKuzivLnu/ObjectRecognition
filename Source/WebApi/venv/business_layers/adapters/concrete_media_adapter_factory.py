from ..factories.abstract_media_adapter_factory import AbstractMediaAdapterFactory
from .jpeg_image_media_adapter import JpegImageMediaAdapter
from .mp4_video_media_adapter import Mp4VideoMediaAdapter
from .abstract_media_adapter import AbstractMediaAdapter


class ConcreteMediaAdapterFactory(AbstractMediaAdapterFactory):
    def createAdapter(self, mediaType: str) -> 'AbstractMediaAdapter':
        if mediaType == 'image/jpeg':
            return JpegImageMediaAdapter()
        if mediaType == 'video/mp4':
            return Mp4VideoMediaAdapter()
        raise ValueError(f"Unsupported media type")
