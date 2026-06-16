/**
 * main.js
 * ============================================================
 * Entry point. Wires every `data-action` button/control in
 * smart_city_mst.html to the corresponding function in app.js /
 * canvas.js, then boots the app with the default preset.
 *
 * The markup deliberately has no inline onclick/oninput — buttons
 * declare *what* they do via `data-action` (+ optional `data-arg`)
 * and this file is the only place that decides *how*, which keeps
 * behaviour out of the HTML and in one well-documented spot.
 * ============================================================
 */

import {
  dom,
  state,
  setMode,
  runAlgo,
  loadPreset,
  openRandomPresetModal,
  closeRandomPresetModal,
  applyRandomPreset,
  resetMST,
  clearAll,
  confirmEdge,
  closeEdgeModal,
  updateRandomPresetLimits,
} from "./app.js";
import { resizeCanvas, initCanvasEvents, zoomIn, zoomOut, resetZoom } from "./canvas.js";

const ACTIONS = {
  "set-mode": (arg) => setMode(arg),
  "run-algo": (arg) => runAlgo(arg),
  "load-preset": (arg) => loadPreset(arg),
  "open-random-modal": () => openRandomPresetModal(),
  "close-random-modal": () => closeRandomPresetModal(),
  "apply-random-preset": () => applyRandomPreset(),
  "reset-mst": () => resetMST(),
  "clear-all": () => clearAll(),
  "confirm-edge": () => confirmEdge(),
  "close-edge-modal": () => closeEdgeModal(),
  "zoom-in": () => zoomIn(),
  "zoom-out": () => zoomOut(),
  "reset-zoom": () => resetZoom(),
};

function bindActionButtons() {
  document.querySelectorAll("[data-action]").forEach((el) => {
    const handler = ACTIONS[el.dataset.action];
    if (!handler) return;
    el.addEventListener("click", () => handler(el.dataset.arg));
  });
}

function bindInlineInputs() {
  dom.speedSlider.addEventListener("input", () => {
    state.animSpeed = parseInt(dom.speedSlider.value);
    dom.speedLabel.textContent = dom.speedSlider.value + "ms";
  });
  dom.randomNodesInput.addEventListener("input", updateRandomPresetLimits);
  dom.randomEdgesInput.addEventListener("input", updateRandomPresetLimits);
}

function init() {
  bindActionButtons();
  bindInlineInputs();
  initCanvasEvents();

  setTimeout(resizeCanvas, 50);
  setTimeout(() => loadPreset("city"), 200);
}

init();
