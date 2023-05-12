from base64 import b64decode

from flask import request, Blueprint
from flask_cors import CORS, cross_origin

from ..business_layers.adapters.concrete_media_adapter_factory import ConcreteMediaAdapterFactory
from ..business_layers.factories.image_processor_plugin_concrete_factory import ImageProcessorPluginConcreteFactory
from ..business_layers.pipelines.media_processing_pipeline import MediaProcessingPipeline
from ..domains.models.media_file import MediaFile
from ..models.enums.pipe_line_plugin_enum import PipeLinePlugin
from ..models.image import Image
from ..models.responses.input_media_process_response import InputMediaProcessResponse

blueprint = Blueprint('blueprint', __name__)

cors = CORS(blueprint)


@blueprint.route('/process', methods=['POST'])
@cross_origin()
def process_media_files():
    request_data = request.get_json()
    files_to_process = request_data['filesToProcess']

    media_files = []
    for f in files_to_process:
        media_type = f['mediaType']
        data = b64decode(f['data'].replace(f"data:{media_type};base64,", ""))
        media_file = MediaFile(data, media_type)
        media_files.append(media_file)

    processor_plugins = request_data['pipelines']

    images = []
    image_processor_plugin_factory = ImageProcessorPluginConcreteFactory()
    media_adapter_factory = ConcreteMediaAdapterFactory()

    for file in media_files:
        media_processing_pipeline = MediaProcessingPipeline(image_processor_plugin_factory, media_adapter_factory, processor_plugins, file)
        image_artifacts = media_processing_pipeline.process()

        mediaAdapter = media_adapter_factory.createAdapter(file.mediaType)
        output_bytes = mediaAdapter.fromImageArtifacts(image_artifacts)
        output_file = MediaFile(output_bytes, file.mediaType)
        images.append(Image(output_file).to_dict())

    response = InputMediaProcessResponse(images)

    return response.to_dict()


@blueprint.route('/pipelines', methods=['GET'])
@cross_origin()
def get_pipelines():
    pipelines = list()
    for pipeline in PipeLinePlugin:
        pipelines.append({pipeline.name: pipeline.value})
    return pipelines
