import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

// --- Scene setup ---
export const scene = new THREE.Scene();
export const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 100);
camera.position.set(0, 1.5, 2.2);

export const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById("scene-container").appendChild(renderer.domElement);

scene.add(new THREE.HemisphereLight(0xffffff, 0x444444, 1.2));
const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
dirLight.position.set(1, 2, 2);
scene.add(dirLight);

let avatarMesh = null;
let morphDict = {};

// Load a GLTF head with ARKit-style morph targets (e.g. a ReadyPlayerMe
// or Mixamo-exported head). Replace 'lumis_head.glb' with your model.
const loader = new GLTFLoader();
loader.load("models/lumis_head.glb", (gltf) => {
  scene.add(gltf.scene);
  gltf.scene.traverse((child) => {
    if (child.isMesh && child.morphTargetDictionary) {
      avatarMesh = child;
      morphDict = child.morphTargetDictionary;
    }
  });
});

function applyBlendshapes(blendshapes) {
  if (!avatarMesh) return;
  for (const [name, value] of Object.entries(blendshapes)) {
    const idx = morphDict[name];
    if (idx !== undefined) {
      avatarMesh.morphTargetInfluences[idx] = value;
    }
  }
}

// --- WebSocket link to avatar_server.py ---
const ws = new WebSocket("ws://localhost:8100/ws/avatar");
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === "animation_frame") {
    applyBlendshapes(data.blendshapes);
  } else if (data.type === "animation_end") {
    applyBlendshapes({}); // reset to neutral
  }
};

function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}
animate();

window.applyBlendshapes = applyBlendshapes;