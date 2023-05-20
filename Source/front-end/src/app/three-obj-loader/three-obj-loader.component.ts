import {
  Component,
  OnInit,
  ElementRef,
  ViewChild,
  AfterViewInit,
  Input,
} from '@angular/core';
import * as THREE from 'three';
import { TrackballControls } from 'three/examples/jsm/controls/TrackballControls';
import { OBJVertexColorLoader } from './obj-vertex-color-loader';
 // Make sure to create this file and add the necessary code
import * as TWEEN from '@tweenjs/tween.js';

@Component({
  selector: 'app-three-obj-loader',
  templateUrl: './three-obj-loader.component.html',
  styleUrls: ['./three-obj-loader.component.scss'],
})
export class ThreeObjLoaderComponent implements OnInit, AfterViewInit {
  @Input() public objFileText: string = '';
  @ViewChild('progressBar', { static: false })
  progressBar!: ElementRef<HTMLProgressElement>;

  container!: HTMLDivElement;
  camera!: THREE.PerspectiveCamera;
  controls!: TrackballControls;
  scene!: THREE.Scene;
  renderer!: THREE.WebGLRenderer;
  raycaster!: THREE.Raycaster;
  objects: THREE.Object3D[] = [];
  windowHalfX: number = window.innerWidth / 2;
  windowHalfY: number = window.innerHeight / 2;

  constructor(private el: ElementRef) {}

  ngOnInit(): void {}

  ngAfterViewInit(): void {
    this.init();
    this.animate();
  }

  init() {
    this.container = this.el.nativeElement;

    this.camera = new THREE.PerspectiveCamera(
      30,
      window.innerWidth / window.innerHeight,
      1,
      20
    );
    this.camera.position.z = -1;
    this.camera.position.y = 5;
    this.camera.position.x = -1;

    this.controls = new TrackballControls(this.camera, this.container);
    this.controls.rotateSpeed = 5;
    this.controls.zoomSpeed = 2;
    this.controls.panSpeed = 0.8;
    this.controls.noZoom = false;
    this.controls.noPan = true;
    this.controls.staticMoving = true;
    this.controls.dynamicDampingFactor = 0;

    this.scene = new THREE.Scene();

    const ambient = new THREE.AmbientLight(0x888888);
    this.scene.add(ambient);

    const directionalLight = new THREE.DirectionalLight(0xffeedd);
    directionalLight.position.set(0, -100, 0);
    this.scene.add(directionalLight);

    const manager = new THREE.LoadingManager();

    const onProgress = (xhr: ProgressEvent) => {
      if (xhr.lengthComputable) {
        const percentComplete = (xhr.loaded / xhr.total) * 100;
        this.progressBar.nativeElement.value = percentComplete;
        this.progressBar.nativeElement.style.display = 'block';
      }
    };

    const onError = (xhr: any) => {};

    const loader = new OBJVertexColorLoader(manager);

    const objContent = this.objFileText;
    const objData = new Blob([objContent], { type: 'text/obj' });
    const objURL = URL.createObjectURL(objData);
    loader.load(objURL, (object) => {
      object.rotation.x = -0.5;
      object.rotation.y = 2;
      object.rotation.z = 0.55;
      this.scene.add(object);
      this.objects.push(object);
    
      this.progressBar.nativeElement.style.display = 'none';
    
      new TWEEN.Tween(this.controls.target)
        .to({
          x: 0.3,
          y: 0.2,
          z: 0.1,
        }, 10)
        .easing(TWEEN.Easing.Quintic.Out)
        .start();
    
      new TWEEN.Tween(this.camera.position)
        .to({
          x: 3.558467649434143,
          y: -2.5468095593526616,
          z: -2.3931801395362005
        }, 150)
        .easing(TWEEN.Easing.Quintic.Out)
        .start();
    
    }, onProgress, onError);
    
    this.renderer = new THREE.WebGLRenderer();
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.renderer.setSize(window.innerWidth/3 + 100, window.innerHeight/3 + 100);
    this.renderer.domElement.style.marginBottom = '300px';
    this.container.appendChild(this.renderer.domElement);
    
    this.raycaster = new THREE.Raycaster();
    
    window.addEventListener('resize', this.onWindowResize.bind(this), false);
    this.renderer.domElement.ondblclick = this.onDoubleClick.bind(this);
    }
    
    onWindowResize() {
      this.windowHalfX = window.innerWidth / 4;
      this.windowHalfY = window.innerHeight / 4;
    
      this.camera.aspect = window.innerWidth / window.innerHeight;
      this.camera.updateProjectionMatrix();
    
      this.controls.handleResize();
    
      this.renderer.setSize(window.innerWidth/3 + 100, window.innerHeight/3 + 100);
    }
    
    onDoubleClick(event: MouseEvent) {
      event.preventDefault();
      if (event.button === 0) {
        const mouse = new THREE.Vector2(
          (event.clientX / this.renderer.domElement.clientWidth) * 2 - 1,
          -(event.clientY / this.renderer.domElement.clientHeight) * 2 + 1
        );
    
        this.raycaster.setFromCamera(mouse, this.camera);
    
        const intersects = this.raycaster.intersectObjects(this.objects, true);
    
        if (intersects.length > 0) {
          new TWEEN.Tween(this.controls.target)
            .to({
              x: intersects[0].point.x,
              y: intersects[0].point.y,
              z: intersects[0].point.z
            }, 250)
            .start();
        }
      }
    }
    
    animate() {
      requestAnimationFrame(() => this.animate());
      TWEEN.update();
      this.controls.update();
      this.render();
    }
    
    render() {
      this.renderer.render(this.scene, this.camera);
    }
    }
    
