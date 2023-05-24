from flask import Flask

from venv.controllers.image_recognition_controller import blueprint

app = Flask(__name__)
app.register_blueprint(blueprint)

if __name__ == '__main__':
    app.run(debug=True)
