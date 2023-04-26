from base64 import b64decode

from flask import jsonify, request, Blueprint
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
    media_files = list(map(lambda f: MediaFile(b64decode(f['data']), f['mediaType']), files_to_process))
    processor_plugins = request_data['pipelines']

    images = []
    image_processor_plugin_factory = ImageProcessorPluginConcreteFactory()
    media_adapter_factory = ConcreteMediaAdapterFactory()

    for file in media_files:
        media_processing_pipeline = MediaProcessingPipeline(image_processor_plugin_factory, media_adapter_factory, processor_plugins, file)
        image_artifacts = media_processing_pipeline.process()
        image_sublist = list(map(lambda ia: Image(ia.data), image_artifacts))
        images.extend(image_sublist)

    response = InputMediaProcessResponse(images)

    return jsonify(response.__dict__)


@blueprint.route('/pipelines', methods=['GET'])
@cross_origin()
def get_pipelines():
    pipelines = list()
    for pipeline in PipeLinePlugin:
        pipelines.append({pipeline.name: pipeline.value})
    return pipelines
