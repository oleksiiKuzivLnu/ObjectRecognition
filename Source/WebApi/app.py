from flask import Flask, jsonify, request
from models.enums.pipe_line_plugin_enum import PipeLinePlugin
from models.image import Image
from models.responses.input_media_process_response import InputMediaProcessResponse

app = Flask(__name__)

#TODO: Create controller and move this logic to here
@app.route('/process', methods=['POST'])
def process_media_files():
    request_data = request.get_json()
    files_to_process = request_data['filesToProcess']

    images = []
    for file in files_to_process:
        if PipeLinePlugin.FaceRecognition in file.requiredPlugins:
            # Implement face recognition pipeline plugin
            pass

        # Implement media file processing logic here

        # Create image object and add to images list
        image = Image(file.data)
        images.append(image)

    response = InputMediaProcessResponse(images)

    return jsonify(response.__dict__)


if __name__ == '__main__':
    app.run(debug=True)
