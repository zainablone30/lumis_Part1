/*
 Pepper's Ghost hologram renderer: renders the avatar 4 times (front, back,
 left, right facing outward) into a cross-shaped layout on screen. Place a
 transparent acrylic/plastic pyramid (45° sides) on top of the display over
 this layout — each face reflects one view, creating a floating 3D illusion.

 Physical build note: cut 4 trapezoids from clear plastic sheet
 (e.g. 1cm top, 6cm bottom, 3.5cm height for a ~5" screen), tape into a
 pyramid, invert, and center over this quad layout.
*/
import * as THREE from "three";
import { scene, camera, renderer } from "./avatar.js";

let hologramMode = false;

window.toggleHologram = function () {
  hologramMode = !hologramMode;
  document.body.classList.toggle("hologram-active", hologramMode);
};

const views = [
  { rotationY: 0,              viewport: [0.25, 0.5, 0.5, 0.5] },   // front (bottom)
  { rotationY: Math.PI,        viewport: [0.25, 0.0, 0.5, 0.5] },   // back (top)
  { rotationY: Math.PI / 2,    viewport: [0.0, 0.25, 0.5, 0.5] },   // left
  { rotationY: -Math.PI / 2,   viewport: [0.5, 0.25, 0.5, 0.5] },   // right
];

const originalRenderFn = renderer.render.bind(renderer);

function renderHologramFrame() {
  const w = window.innerWidth, h = window.innerHeight;
  renderer.setScissorTest(true);

  for (const v of views) {
    const [x, y, vw, vh] = v.viewport;
    renderer.setViewport(x * w, y * h, vw * w, vh * h);
    renderer.setScissor(x * w, y * h, vw * w, vh * h);

    scene.rotation.y = v.rotationY;
    originalRenderFn(scene, camera);
  }
  renderer.setScissorTest(false);
}

function loop() {
  requestAnimationFrame(loop);
  if (hologramMode) renderHologramFrame();
}
loop();