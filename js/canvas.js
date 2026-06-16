/**
 * canvas.js
 * ============================================================
 * Everything that touches <canvas id="network-canvas">: drawing
 * the graph, hit-testing clicks against nodes/edges, pan & zoom,
 * and the click/drag handlers that let the user build a graph by
 * hand. Reads/writes `state` and `dom` from app.js; never decides
 * algorithm logic itself.
 * ============================================================
 */

import { state, dom, log, openEdgeModal, updateCounts, updateEdgeTable } from "./app.js";

// NOTE: app.js and canvas.js import each other (app.js needs draw(),
// canvas.js needs state/dom/log). That's fine for code used inside
// functions, which only runs after both modules have finished loading —
// but top-level module code runs *during* loading, while the cycle is
// still being resolved, so it must not dereference the other module's
// bindings yet. That's why this grabs the canvas element itself
// directly instead of going through app.js's `dom.canvas`.
const canvasEl = document.getElementById("network-canvas");
export const ctx = canvasEl.getContext("2d");

let panCandidate = null;
let panDragging = false;
let suppressClick = false;

// ------------------------------------------------------------
// Rendering
// ------------------------------------------------------------

export function resizeCanvas() {
  canvasEl.width = canvasEl.offsetWidth;
  canvasEl.height = canvasEl.offsetHeight;
  draw();
}

export function draw() {
  const { nodes, edges, mstEdges, mstAlgo, edgeStart, scale, offsetX, offsetY } = state;

  ctx.clearRect(0, 0, canvasEl.width, canvasEl.height);
  ctx.save();
  ctx.translate(offsetX, offsetY);
  ctx.scale(scale, scale);

  drawGrid();
  drawEdges(nodes, edges, mstEdges, mstAlgo);
  drawNodes(nodes, mstEdges, mstAlgo, edgeStart);

  ctx.restore();
}

function drawGrid() {
  const { scale, offsetX, offsetY } = state;
  ctx.fillStyle = "rgba(10,58,92,0.25)";
  const step = 40;
  for (let x = -offsetX / scale; x < (canvasEl.width - offsetX) / scale; x += step) {
    for (let y = -offsetY / scale; y < (canvasEl.height - offsetY) / scale; y += step) {
      ctx.beginPath();
      ctx.arc(x, y, 1, 0, Math.PI * 2);
      ctx.fill();
    }
  }
}

const ALGO_COLORS = {
  kruskal: { from: "#ff6b35", to: "#ffcc00", solid: "#ff6b35" },
  brute: { from: "#b44fff", to: "#ff4488", solid: "#b44fff" },
  prim: { from: "#00d4ff", to: "#39ff14", solid: "#00d4ff" },
};
function algoColors(mstAlgo) {
  return ALGO_COLORS[mstAlgo] || ALGO_COLORS.prim;
}
function isInMst(mstEdges, e) {
  return mstEdges.some((me) => (me.from === e.from && me.to === e.to) || (me.from === e.to && me.to === e.from));
}

function drawEdges(nodes, edges, mstEdges, mstAlgo) {
  edges.forEach((e) => {
    const n1 = nodes.find((n) => n.id === e.from);
    const n2 = nodes.find((n) => n.id === e.to);
    if (!n1 || !n2) return;
    if (isInMst(mstEdges, e)) drawMstEdge(n1, n2, e, mstAlgo);
    else drawPlainEdge(n1, n2, e);
  });
}

function drawMstEdge(n1, n2, e, mstAlgo) {
  const colors = algoColors(mstAlgo);
  ctx.beginPath();
  const grad = ctx.createLinearGradient(n1.x, n1.y, n2.x, n2.y);
  grad.addColorStop(0, colors.from);
  grad.addColorStop(1, colors.to);
  ctx.strokeStyle = grad;
  ctx.lineWidth = 3.5;
  ctx.shadowColor = colors.solid;
  ctx.shadowBlur = 12;
  ctx.moveTo(n1.x, n1.y);
  ctx.lineTo(n2.x, n2.y);
  ctx.stroke();
  ctx.shadowBlur = 0;

  const mx = (n1.x + n2.x) / 2;
  const my = (n1.y + n2.y) / 2;
  ctx.fillStyle = mstAlgo === "prim" || !mstAlgo ? "#39ff14" : colors.solid;
  ctx.font = "bold 11px Orbitron";
  ctx.textAlign = "center";
  ctx.fillText(e.weight, mx, my - 6);
}

function drawPlainEdge(n1, n2, e) {
  ctx.beginPath();
  ctx.strokeStyle = "rgba(20,70,110,0.7)";
  ctx.lineWidth = 1.5;
  ctx.setLineDash([5, 5]);
  ctx.moveTo(n1.x, n1.y);
  ctx.lineTo(n2.x, n2.y);
  ctx.stroke();
  ctx.setLineDash([]);

  if (e.animating) {
    ctx.beginPath();
    ctx.strokeStyle = "rgba(0,212,255,0.65)";
    ctx.lineWidth = 2.5;
    ctx.moveTo(n1.x, n1.y);
    ctx.lineTo(n2.x, n2.y);
    ctx.stroke();
  }

  const mx = (n1.x + n2.x) / 2;
  const my = (n1.y + n2.y) / 2;
  ctx.fillStyle = "rgba(74,122,155,0.9)";
  ctx.font = "10px Share Tech Mono";
  ctx.textAlign = "center";
  ctx.fillText(e.weight, mx, my - 5);
}

function drawNodes(nodes, mstEdges, mstAlgo, edgeStart) {
  nodes.forEach((n) => {
    const isSelected = edgeStart === n.id;
    const isMSTNode = mstEdges.some((e) => e.from === n.id || e.to === n.id);
    const colors = algoColors(mstAlgo);

    if (isSelected || isMSTNode) {
      ctx.beginPath();
      ctx.arc(n.x, n.y, 22, 0, Math.PI * 2);
      ctx.strokeStyle = isSelected
        ? "rgba(255,204,0,0.4)"
        : mstAlgo === "kruskal"
          ? "rgba(255,107,53,0.3)"
          : "rgba(0,212,255,0.3)";
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }

    ctx.beginPath();
    ctx.arc(n.x, n.y, 16, 0, Math.PI * 2);
    const g = ctx.createRadialGradient(n.x - 4, n.y - 4, 2, n.x, n.y, 16);
    if (isSelected) {
      g.addColorStop(0, "#806000");
      g.addColorStop(1, "#241a00");
    } else if (isMSTNode) {
      if (mstAlgo === "kruskal") {
        g.addColorStop(0, "#7a2f10");
        g.addColorStop(1, "#1a0800");
      } else if (mstAlgo === "brute") {
        g.addColorStop(0, "#55168a");
        g.addColorStop(1, "#150020");
      } else {
        g.addColorStop(0, "#003d50");
        g.addColorStop(1, "#001a22");
      }
    } else {
      g.addColorStop(0, "#1a3a5c");
      g.addColorStop(1, "#050e18");
    }
    ctx.fillStyle = g;
    ctx.fill();
    ctx.strokeStyle = isSelected ? "#ffcc00" : isMSTNode ? colors.solid : "#1a5c80";
    ctx.lineWidth = isSelected ? 2.5 : isMSTNode ? 2 : 1.5;
    ctx.shadowColor = isSelected ? "#ffcc00" : isMSTNode ? colors.solid : "transparent";
    ctx.shadowBlur = isMSTNode || isSelected ? 10 : 0;
    ctx.stroke();
    ctx.shadowBlur = 0;

    ctx.fillStyle = isSelected ? "#ffcc00" : isMSTNode ? colors.solid : "#4a7a9b";
    ctx.font = "12px Arial";
    ctx.textAlign = "center";
    ctx.fillText("📡", n.x, n.y + 4);

    ctx.fillStyle = isSelected ? "#ffcc00" : isMSTNode ? "#ffffff" : "#7ab0d0";
    ctx.font = "bold 9px Orbitron";
    ctx.textAlign = "center";
    ctx.fillText(n.label, n.x, n.y + 28);
  });
}

// ------------------------------------------------------------
// Hit-testing (pure helpers, used by both editing and panning)
// ------------------------------------------------------------

function getNodeAt(x, y) {
  return state.nodes.find((n) => Math.hypot(n.x - x, n.y - y) < 18) || null;
}
function getEdgeAt(x, y) {
  for (const e of state.edges) {
    const n1 = state.nodes.find((n) => n.id === e.from);
    const n2 = state.nodes.find((n) => n.id === e.to);
    if (!n1 || !n2) continue;
    if (pointToSegmentDist(x, y, n1.x, n1.y, n2.x, n2.y) < 8) return e;
  }
  return null;
}
function pointToSegmentDist(px, py, ax, ay, bx, by) {
  const dx = bx - ax;
  const dy = by - ay;
  if (dx === 0 && dy === 0) return Math.hypot(px - ax, py - ay);
  const t = Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)));
  return Math.hypot(px - ax - t * dx, py - ay - t * dy);
}

function toWorld(e) {
  const rect = canvasEl.getBoundingClientRect();
  return {
    x: (e.clientX - rect.left - state.offsetX) / state.scale,
    y: (e.clientY - rect.top - state.offsetY) / state.scale,
  };
}

// ------------------------------------------------------------
// Zoom & pan
// ------------------------------------------------------------

export function zoomIn() {
  state.scale = Math.min(state.scale * 1.2, 3);
  draw();
}
export function zoomOut() {
  state.scale = Math.max(state.scale / 1.2, 0.3);
  draw();
}
export function resetZoom() {
  state.scale = 1;
  state.offsetX = 0;
  state.offsetY = 0;
  draw();
}

function startPan(e) {
  panCandidate = { x: e.clientX, y: e.clientY, offsetX: state.offsetX, offsetY: state.offsetY };
  panDragging = false;
}
function updatePan(e) {
  if (!panCandidate) return;
  const dx = e.clientX - panCandidate.x;
  const dy = e.clientY - panCandidate.y;
  if (!panDragging && Math.hypot(dx, dy) > 4) panDragging = true;
  if (panDragging) {
    state.offsetX = panCandidate.offsetX + dx;
    state.offsetY = panCandidate.offsetY + dy;
    draw();
  }
}
function endPan() {
  if (panCandidate && panDragging) suppressClick = true;
  panCandidate = null;
  panDragging = false;
}

// ------------------------------------------------------------
// Graph editing via canvas clicks (add node / add edge / delete)
// ------------------------------------------------------------

function handleClick(e) {
  if (suppressClick) {
    suppressClick = false;
    return;
  }
  if (state.isRunning) return;
  const { x: wx, y: wy } = toWorld(e);

  if (state.mode === "node") handleAddNodeClick(wx, wy);
  else if (state.mode === "edge") handleAddEdgeClick(wx, wy);
  else if (state.mode === "delete") handleDeleteClick(wx, wy);
}

function handleAddNodeClick(wx, wy) {
  for (const n of state.nodes) {
    if (Math.hypot(n.x - wx, n.y - wy) < 36) {
      log("Node too close to existing node", "warn");
      return;
    }
  }
  const label = "S" + (state.nodeIdCounter + 1);
  state.nodes.push({ id: ++state.nodeIdCounter, x: wx, y: wy, label });
  log(`Added sensor node ${label}`, "info");
  updateCounts();
  draw();
}

function handleAddEdgeClick(wx, wy) {
  const hit = getNodeAt(wx, wy);
  if (!hit) {
    state.edgeStart = null;
    draw();
    return;
  }
  if (!state.edgeStart) {
    state.edgeStart = hit.id;
    log(`Select target node for connection from ${hit.label}`, "info");
    draw();
    return;
  }
  if (hit.id === state.edgeStart) {
    state.edgeStart = null;
    draw();
    return;
  }
  if (state.edges.some((ex) => (ex.from === state.edgeStart && ex.to === hit.id) || (ex.from === hit.id && ex.to === state.edgeStart))) {
    log("Connection already exists", "warn");
    state.edgeStart = null;
    draw();
    return;
  }
  const fromNode = state.nodes.find((n) => n.id === state.edgeStart);
  openEdgeModal(fromNode, hit);
  state.edgeStart = null;
}

function handleDeleteClick(wx, wy) {
  const hitNode = getNodeAt(wx, wy);
  if (hitNode) {
    state.nodes = state.nodes.filter((n) => n.id !== hitNode.id);
    state.edges = state.edges.filter((ex) => ex.from !== hitNode.id && ex.to !== hitNode.id);
    state.mstEdges = state.mstEdges.filter((ex) => ex.from !== hitNode.id && ex.to !== hitNode.id);
    log(`Deleted node ${hitNode.label}`, "warn");
    updateCounts();
    updateEdgeTable();
    draw();
    return;
  }
  const hitEdge = getEdgeAt(wx, wy);
  if (hitEdge) {
    const n1 = state.nodes.find((n) => n.id === hitEdge.from);
    const n2 = state.nodes.find((n) => n.id === hitEdge.to);
    state.edges = state.edges.filter((ex) => ex !== hitEdge);
    state.mstEdges = state.mstEdges.filter(
      (ex) => !((ex.from === hitEdge.from && ex.to === hitEdge.to) || (ex.from === hitEdge.to && ex.to === hitEdge.from)),
    );
    log(`Deleted edge ${n1.label}–${n2.label}`, "warn");
    updateCounts();
    updateEdgeTable();
    draw();
  }
}

function handleMouseMove(e) {
  const { x: wx, y: wy } = toWorld(e);
  const hit = getNodeAt(wx, wy);
  if (hit) {
    const rect = canvasEl.getBoundingClientRect();
    const deg = state.edges.filter((ex) => ex.from === hit.id || ex.to === hit.id).length;
    dom.tooltip.style.display = "block";
    dom.tooltip.style.left = e.clientX - rect.left + 15 + "px";
    dom.tooltip.style.top = e.clientY - rect.top + 10 + "px";
    dom.tooltip.textContent = `${hit.label} · Connections: ${deg}`;
  } else {
    dom.tooltip.style.display = "none";
  }
}

/** Wires up every canvas-level DOM event listener. Call once at startup. */
export function initCanvasEvents() {
  canvasEl.addEventListener("click", handleClick);
  canvasEl.addEventListener("mousemove", handleMouseMove);
  canvasEl.addEventListener("mousemove", updatePan);
  canvasEl.addEventListener("mouseup", endPan);
  canvasEl.addEventListener("mouseleave", endPan);

  canvasEl.addEventListener(
    "wheel",
    (e) => {
      e.preventDefault();
      const rect = canvasEl.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      const factor = e.deltaY < 0 ? 1.12 : 0.88;
      const newScale = Math.max(0.3, Math.min(3, state.scale * factor));
      state.offsetX = mx - (mx - state.offsetX) * (newScale / state.scale);
      state.offsetY = my - (my - state.offsetY) * (newScale / state.scale);
      state.scale = newScale;
      draw();
    },
    { passive: false },
  );

  canvasEl.addEventListener("mousedown", (e) => {
    if (e.button === 1 || (e.button === 0 && e.altKey)) {
      startPan(e);
      e.preventDefault();
      return;
    }
    if (e.button !== 0) return;
    const { x: wx, y: wy } = toWorld(e);
    if (getNodeAt(wx, wy) || getEdgeAt(wx, wy)) return; // let click handle it, don't start a pan
    startPan(e);
  });

  window.addEventListener("resize", resizeCanvas);
}
