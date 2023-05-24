// @ts-nocheck
import * as THREE from 'three';

export class OBJVertexColorLoader {
  manager: THREE.LoadingManager;
  materials: any;
  path!: string;

  constructor(manager?: THREE.LoadingManager) {
    this.manager = manager !== undefined ? manager : THREE.DefaultLoadingManager;
    this.materials = null;
  }

  load(
    url: string,
    onLoad: (object: THREE.Group) => void,
    onProgress?: (event: ProgressEvent) => void,
    onError?: (event: ErrorEvent) => void
  ): void {
    const scope = this;

    const loader = new THREE.FileLoader(scope.manager);

    loader.setPath(this.path);

    loader.load(
      url,
      (text) => {
        // @ts-ignore
        onLoad(scope.parse(text));
      },
      onProgress,
      onError
    );
  }

  setPath(value: string): void {
    this.path = value;
  }

  parse(text: string): THREE.Group {
    var container = new THREE.Group();
        var geometry = new THREE.Geometry();
        var vertices = [];
        var vertexColors = [];
        var faces = [];

        // v float float float float float float (vertex with rgb) 
        var vertex_colour_pattern = /^v\s+([\d|\.|\+|\-|e|E]+)\s+([\d|\.|\+|\-|e|E]+)\s+([\d|\.|\+|\-|e|E]+)\s+([\d|\.|\+|\-|e|E]+)\s+([\d|\.|\+|\-|e|E]+)\s+([\d|\.|\+|\-|e|E]+)/;

        // f vertex vertex vertex ...
        var face_pattern1 = /^f\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)(?:\s+(-?\d+))?/;

        var lines = text.split('\n');

        for (var i = 0; i < lines.length; i++) {
            
            var line = lines[i];
            line = line.trim();
            var result;

            if (line.length === 0 || line.charAt(0) === '#') {
                continue;
            } else if ((result = vertex_colour_pattern.exec(line)) !== null) {
                vertices.push(
                    new THREE.Vector3(parseFloat(result[1]), parseFloat(result[2]), parseFloat(result[3]))
                );
                vertexColors.push(new THREE.Color(parseFloat(result[4]), parseFloat(result[5]), parseFloat(result[6])));
            } else if ((result = face_pattern1.exec(line)) !== null) {
                faces.push(new THREE.Face3(result[1] - 1, result[2] - 1, result[3] - 1));
            }
        }

        for (var i = 0; i < vertices.length; i++) {
            geometry.vertices.push(vertices[i]);
        }
        for (var i = 0; i < faces.length; i++) {
            faces[i].vertexColors[0] = vertexColors[faces[i].a];
            faces[i].vertexColors[1] = vertexColors[faces[i].b];
            faces[i].vertexColors[2] = vertexColors[faces[i].c];
            geometry.faces.push(faces[i]);
        }

        var material = new THREE.MeshBasicMaterial({ vertexColors: THREE.VertexColors });

        var mesh = new THREE.Mesh(geometry, material);
        container.add(mesh);

        return container;
  }
}
