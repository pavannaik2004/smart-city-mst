/**
 * app.js
 * ============================================================
 * The application layer: shared state, DOM references, logging,
 * modals, presets, and the "run an algorithm" controller. Canvas
 * drawing/hit-testing/pan-zoom lives in canvas.js; algorithm
 * internals live in algorithms/*.js + datastructures/*.js. This
 * file is the glue between all of them and the page's buttons.
 * ============================================================
 */

import { draw } from "./canvas.js";
import { Graph } from "./datastructures/Graph.js";
import { primMST } from "./algorithms/prims.js";
import { kruskalMST } from "./algorithms/kruskals.js";
import { bruteForceMST } from "./algorithms/bruteforce.js";
import { computeAllComplexities, formatOps, renderComplexityPanel } from "./complexityAnalyzer.js";
import { runTimedAlgorithm, compareToPrevious } from "./timeAnalyzer.js";

export const MAX_RANDOM_NODES = 12;

// ------------------------------------------------------------
// State — single source of truth for the graph + UI flags.
// Every other module reads/writes this instead of keeping its
// own copy, so nothing can drift out of sync.
//   node: { id, x, y, label }
//   edge: { from, to, weight, animating }
// ------------------------------------------------------------
export const state = {
  nodes: [],
  edges: [],
  nodeIdCounter: 0,
  mode: "node", // 'node' | 'edge' | 'delete'
  edgeStart: null,
  animSpeed: 600,
  isRunning: false,
  mstEdges: [],
  mstAlgo: "",
  pendingEdge: null,
  scale: 1,
  offsetX: 0,
  offsetY: 0,
};

// ------------------------------------------------------------
// DOM references, gathered once.
// ------------------------------------------------------------
export const dom = {
  canvas: document.getElementById("network-canvas"),
  tooltip: document.getElementById("tooltip"),
  canvasHint: document.getElementById("canvas-hint"),
  runningLabel: document.getElementById("running-label"),

  btnAddNode: document.getElementById("btn-add-node"),
  btnAddEdge: document.getElementById("btn-add-edge"),
  modeDisplay: document.getElementById("mode-display"),

  speedSlider: document.getElementById("speed-slider"),
  speedLabel: document.getElementById("speed-label"),

  nodeCount: document.getElementById("node-count"),
  edgeCount: document.getElementById("edge-count"),
  mstCostSidebar: document.getElementById("mst-cost-sidebar"),

  resAlgo: document.getElementById("res-algo"),
  resCost: document.getElementById("res-cost"),
  resEdges: document.getElementById("res-edges"),
  resSteps: document.getElementById("res-steps"),
  resTime: document.getElementById("res-time"),
  progressFill: document.getElementById("progress-fill"),

  complexityBody: document.getElementById("complexity-body"),

  edgeTableBody: document.getElementById("edge-table-body"),
  logArea: document.getElementById("log-area"),

  edgeModal: document.getElementById("edge-modal"),
  edgeWeightInput: document.getElementById("edge-weight-input"),
  modalFrom: document.getElementById("modal-from"),
  modalTo: document.getElementById("modal-to"),

  randomModal: document.getElementById("random-modal"),
  randomNodesInput: document.getElementById("random-nodes-input"),
  randomEdgesInput: document.getElementById("random-edges-input"),
  randomEdgesHelp: document.getElementById("random-edges-help"),
};

// ------------------------------------------------------------
// Logging — the "Algorithm Log" panel.
// ------------------------------------------------------------
export function log(msg, type = "") {
  const span = document.createElement("span");
  span.className = "log-line " + type;
  span.textContent = "> " + msg;
  dom.logArea.appendChild(span);
  dom.logArea.appendChild(document.createElement("br"));
  dom.logArea.scrollTop = dom.logArea.scrollHeight;
}
export function clearLog() {
  dom.logArea.innerHTML = "";
}

export function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ------------------------------------------------------------
// UI state — edit mode, counters, tables, reset/clear.
// ------------------------------------------------------------
const MODE_HINTS = {
  node: "Click canvas to place sensor nodes",
  edge: "Click two nodes to connect them",
  delete: "Click node or edge to delete",
};
const MODE_LABELS = { node: "ADD NODE", edge: "ADD CONNECTION", delete: "DELETE" };

export function setMode(m) {
  state.mode = m;
  state.edgeStart = null;

  [dom.btnAddNode, dom.btnAddEdge].forEach((btn) => btn.classList.remove("active"));
  if (m === "node") dom.btnAddNode.classList.add("active");
  if (m === "edge") dom.btnAddEdge.classList.add("active");

  dom.modeDisplay.textContent = MODE_LABELS[m] || m.toUpperCase();
  dom.canvasHint.textContent = MODE_HINTS[m] || "";
  draw();
}

export function updateCounts() {
  dom.nodeCount.textContent = state.nodes.length;
  dom.edgeCount.textContent = state.edges.length;
  renderComplexityPanel(state.nodes.length, state.edges.length);
}

export function updateEdgeTable() {
  if (state.edges.length === 0) {
    dom.edgeTableBody.innerHTML =
      '<tr><td colspan="4" style="color:var(--muted);text-align:center;padding:10px;">No edges yet</td></tr>';
    return;
  }
  dom.edgeTableBody.innerHTML = state.edges
    .map((e) => {
      const n1 = state.nodes.find((n) => n.id === e.from);
      const n2 = state.nodes.find((n) => n.id === e.to);
      const isMST = state.mstEdges.some(
        (me) => (me.from === e.from && me.to === e.to) || (me.from === e.to && me.to === e.from),
      );
      const cls = isMST ? "mst-edge" + (state.mstAlgo === "kruskal" ? " kruskal" : "") : "";
      return `<tr class="${cls}">
      <td>${n1 ? n1.label : "?"}</td><td>${n2 ? n2.label : "?"}</td><td>${e.weight}</td>
      <td>${isMST ? "✓" : ""}</td>
    </tr>`;
    })
    .join("");
}

export function resetMST() {
  state.mstEdges = [];
  state.mstAlgo = "";
  dom.runningLabel.textContent = "";
  dom.resCost.textContent = "—";
  dom.resEdges.textContent = "—";
  dom.resAlgo.textContent = "—";
  dom.resTime.textContent = "—";
  dom.resSteps.textContent = "—";
  dom.mstCostSidebar.textContent = "—";
  dom.progressFill.style.width = "0%";
  updateEdgeTable();
  draw();
}

export function clearAll() {
  state.nodes = [];
  state.edges = [];
  state.nodeIdCounter = 0;
  state.edgeStart = null;
  state.isRunning = false;
  resetMST();
  clearLog();
  log("Graph cleared", "warn");
  updateCounts();
  draw();
}

// ------------------------------------------------------------
// Edge-weight modal
// ------------------------------------------------------------
export function openEdgeModal(fromNode, toNode) {
  state.pendingEdge = { from: fromNode.id, to: toNode.id };
  dom.modalFrom.textContent = fromNode.label;
  dom.modalTo.textContent = toNode.label;
  dom.edgeWeightInput.value = Math.floor(Math.random() * 50) + 5;
  dom.edgeModal.classList.add("show");
}

export function confirmEdge() {
  const w = parseInt(dom.edgeWeightInput.value);
  if (isNaN(w) || w < 1) return;
  const { from, to } = state.pendingEdge;
  state.edges.push({ from, to, weight: w, animating: false });

  const n1 = state.nodes.find((n) => n.id === from);
  const n2 = state.nodes.find((n) => n.id === to);
  log(`Added edge ${n1.label}–${n2.label} cost=${w}`, "edge");

  closeEdgeModal();
  updateCounts();
  updateEdgeTable();
  draw();
}

export function closeEdgeModal() {
  dom.edgeModal.classList.remove("show");
  state.pendingEdge = null;
  state.edgeStart = null;
  draw();
}

// ------------------------------------------------------------
// Random-preset modal
// ------------------------------------------------------------
export function openRandomPresetModal() {
  dom.randomNodesInput.value = Math.min(8, MAX_RANDOM_NODES);
  dom.randomEdgesInput.value = 12;
  updateRandomPresetLimits();
  dom.randomModal.classList.add("show");
}
export function closeRandomPresetModal() {
  dom.randomModal.classList.remove("show");
}
export function updateRandomPresetLimits() {
  let n = parseInt(dom.randomNodesInput.value);
  if (isNaN(n)) n = 2;
  n = Math.max(2, Math.min(MAX_RANDOM_NODES, n));
  dom.randomNodesInput.value = n;

  const minEdges = Math.max(1, n - 1);
  const maxEdges = (n * (n - 1)) / 2;
  dom.randomEdgesInput.min = minEdges;
  dom.randomEdgesInput.max = maxEdges;

  let e = parseInt(dom.randomEdgesInput.value);
  if (isNaN(e)) e = minEdges;
  e = Math.max(minEdges, Math.min(maxEdges, e));
  dom.randomEdgesInput.value = e;

  dom.randomEdgesHelp.textContent = `Allowed edges: ${minEdges} to ${maxEdges}`;
}
export function applyRandomPreset() {
  updateRandomPresetLimits();
  const n = parseInt(dom.randomNodesInput.value);
  const e = parseInt(dom.randomEdgesInput.value);
  closeRandomPresetModal();
  loadPreset("random", { nodes: n, edges: e });
}

// ------------------------------------------------------------
// Presets — canned graphs + random graph generator
// ------------------------------------------------------------
export function loadPreset(type, options = {}) {
  clearAll();
  const W = dom.canvas.width / state.scale;
  const H = dom.canvas.height / state.scale;
  const cx = W / 2;
  const cy = H / 2;

  if (type === "city") {
    const positions = [
      [cx - 200, cy - 150], [cx, cy - 180], [cx + 200, cy - 150],
      [cx - 220, cy], [cx + 220, cy],
      [cx - 200, cy + 150], [cx, cy + 170], [cx + 200, cy + 150],
    ];
    positions.forEach(([x, y], i) =>
      state.nodes.push({ id: ++state.nodeIdCounter, x, y, label: "S" + (i + 1) }),
    );
    const edgeDefs = [
      [1, 2, 15], [2, 3, 20], [1, 4, 12], [2, 5, 18], [3, 5, 14],
      [4, 6, 16], [4, 5, 30], [5, 7, 22], [6, 7, 10], [7, 8, 13],
      [5, 8, 25], [6, 8, 28], [3, 8, 35],
    ];
    edgeDefs.forEach(([f, t, w]) => state.edges.push({ from: f, to: t, weight: w, animating: false }));
    log("Loaded: City Grid (8 sensors)", "info");
  } else if (type === "star") {
    state.nodes.push({ id: ++state.nodeIdCounter, x: cx, y: cy, label: "HUB" });
    const r = 160;
    for (let i = 0; i < 6; i++) {
      const a = (i / 6) * Math.PI * 2 - Math.PI / 2;
      state.nodes.push({
        id: ++state.nodeIdCounter,
        x: cx + r * Math.cos(a),
        y: cy + r * Math.sin(a),
        label: "S" + (i + 1),
      });
    }
    for (let i = 2; i <= 7; i++)
      state.edges.push({ from: 1, to: i, weight: Math.floor(Math.random() * 30) + 10, animating: false });
    state.edges.push(
      { from: 2, to: 3, weight: 45, animating: false },
      { from: 3, to: 4, weight: 38, animating: false },
      { from: 5, to: 6, weight: 42, animating: false },
    );
    log("Loaded: Hub & Spoke topology", "info");
  } else if (type === "random") {
    const count = Math.max(2, Math.min(MAX_RANDOM_NODES, options.nodes || 7));
    const minEdges = Math.max(1, count - 1);
    const maxEdges = (count * (count - 1)) / 2;
    const edgeCount = Math.max(minEdges, Math.min(options.edges || Math.round(count * 1.6), maxEdges));
    createRandomGraph(count, edgeCount, W, H);
    log(`Loaded: Random sensor network (${count} nodes, ${edgeCount} edges)`, "info");
  }

  updateCounts();
  updateEdgeTable();
  draw();
}

function createRandomGraph(count, edgeCount, W, H) {
  const marginX = 80, marginY = 70, minDist = 40;
  const positions = [];
  for (let i = 0; i < count; i++) {
    let placed = false;
    for (let attempt = 0; attempt < 40; attempt++) {
      const x = marginX + Math.random() * (W - marginX * 2);
      const y = marginY + Math.random() * (H - marginY * 2);
      if (positions.every((p) => Math.hypot(p.x - x, p.y - y) > minDist)) {
        positions.push({ x, y });
        placed = true;
        break;
      }
    }
    if (!placed)
      positions.push({ x: marginX + Math.random() * (W - marginX * 2), y: marginY + Math.random() * (H - marginY * 2) });
  }

  positions.forEach((p, i) =>
    state.nodes.push({ id: ++state.nodeIdCounter, x: p.x, y: p.y, label: "S" + (i + 1) }),
  );

  const edgeSet = new Set();
  const addEdge = (a, b) => {
    const key = a < b ? `${a}-${b}` : `${b}-${a}`;
    if (edgeSet.has(key)) return false;
    edgeSet.add(key);
    state.edges.push({ from: a, to: b, weight: Math.floor(Math.random() * 60) + 5, animating: false });
    return true;
  };

  // Guarantee connectivity first: attach every node to a random earlier one.
  for (let i = 1; i < state.nodes.length; i++) {
    const target = Math.floor(Math.random() * i);
    addEdge(state.nodes[i].id, state.nodes[target].id);
  }

  const pairs = [];
  for (let i = 0; i < state.nodes.length; i++) {
    for (let j = i + 1; j < state.nodes.length; j++) {
      const a = state.nodes[i].id, b = state.nodes[j].id;
      const key = a < b ? `${a}-${b}` : `${b}-${a}`;
      if (!edgeSet.has(key)) pairs.push([a, b]);
    }
  }

  while (state.edges.length < edgeCount && pairs.length > 0) {
    const idx = Math.floor(Math.random() * pairs.length);
    const [a, b] = pairs.splice(idx, 1)[0];
    addEdge(a, b);
  }
}

// ------------------------------------------------------------
// Run controller — validates the graph, runs the chosen
// algorithm, and reports measured time against the theoretical
// estimate from complexityAnalyzer.js / timeAnalyzer.js.
// ------------------------------------------------------------
const ALGORITHMS = {
  prim: { run: primMST, label: "PRIM'S", color: "var(--accent)" },
  kruskal: { run: kruskalMST, label: "KRUSKAL'S", color: "var(--accent2)" },
  brute: { run: bruteForceMST, label: "BRUTE FORCE", color: "#b44fff" },
};

// Last measured run per algorithm, used by timeAnalyzer.js to report
// how runtime grew between this run and the previous one for the
// same algorithm (e.g. after you add a few more sensors).
const runHistory = {};

export async function runAlgo(algoKey) {
  if (state.isRunning) return;
  const algo = ALGORITHMS[algoKey];
  if (!algo) return;

  if (state.nodes.length < 2) {
    log("Need at least 2 sensor nodes", "warn");
    return;
  }
  if (state.edges.length < 1) {
    log("Need at least 1 edge/connection", "warn");
    return;
  }
  if (!Graph.fromNodesEdges(state.nodes, state.edges).isConnected()) {
    log("Graph is not connected — MST not possible", "warn");
    return;
  }

  state.isRunning = true;
  state.mstEdges = [];
  state.mstAlgo = algoKey;
  clearLog();

  dom.progressFill.style.width = "0%";
  dom.resAlgo.textContent = algo.label;
  dom.resAlgo.style.color = algo.color;
  dom.runningLabel.textContent = "⚡ RUNNING...";
  dom.resCost.textContent = "...";
  dom.resSteps.textContent = "...";
  dom.resTime.textContent = "...";

  const estimate = computeAllComplexities(state.nodes.length, state.edges.length)[algoKey];
  log(
    `Theoretical estimate for V=${state.nodes.length}, E=${state.edges.length}: ` +
      `~${formatOps(estimate.ops)} basic operations (${estimate.formula})`,
    "info",
  );

  const { elapsedMs } = await runTimedAlgorithm(algo.run);

  const totalCost = state.mstEdges.reduce((s, e) => s + e.weight, 0);
  dom.resCost.textContent = totalCost + " units";
  dom.resEdges.textContent = state.mstEdges.length;
  dom.resTime.textContent = elapsedMs.toFixed(1) + " ms";
  dom.mstCostSidebar.textContent = totalCost;
  dom.progressFill.style.width = "100%";
  dom.runningLabel.textContent = "✓ COMPLETE";

  log(`MST COMPLETE — Total cost: ${totalCost} units`, "success");
  log(`Measured time: ${elapsedMs.toFixed(1)} ms vs. ~${formatOps(estimate.ops)} estimated operations`, "info");

  const growth = compareToPrevious(runHistory, algoKey, state.nodes.length, state.edges.length, elapsedMs);
  if (growth) {
    log(
      `Growth vs. last ${algo.label} run: input ×${growth.sizeRatio.toFixed(2)}, time ×${growth.timeRatio.toFixed(2)}`,
      "info",
    );
  }
  updateEdgeTable();

  state.isRunning = false;
}
