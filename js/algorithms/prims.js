/**
 * algorithms/prims.js
 * ============================================================
 * Prim's algorithm — grows a single tree one cheapest edge at a
 * time, always crossing the "cut" between the tree built so far
 * and everything still outside it. The Cut Property guarantees
 * that the cheapest edge crossing any cut belongs to *some* MST,
 * which is why this greedy choice is always safe.
 *
 * Data structures used:
 *   - Graph (datastructures/Graph.js)   — adjacency list, O(deg) neighbour lookup
 *   - MinHeap (datastructures/MinHeap.js) — frontier edges ordered by weight
 *
 * Each node, once added to the tree, pushes its incident edges onto
 * the heap; "lazy deletion" (skipping popped entries whose far end is
 * already visited) avoids needing a decrease-key operation. Every
 * edge is pushed/popped at most once, each costing O(log V), giving:
 *   Time:  O((V + E) log V)
 *   Space: O(V + E)
 * ============================================================
 */

import { state, dom, log } from "../app.js";
import { draw } from "../canvas.js";
import { Graph } from "../datastructures/Graph.js";
import { MinHeap } from "../datastructures/MinHeap.js";

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function primMST() {
  log("=== PRIM'S ALGORITHM ===", "info");
  log("Data Structures: Graph (adjacency list) + Min-Heap (priority queue)", "info");
  log("Complexity: O((V + E) log V)", "info");
  log("", "");

  const { nodes, edges } = state;
  const graph = Graph.fromNodesEdges(nodes, edges);

  const visited = new Set();
  const start = nodes[0];
  visited.add(start.id);
  log(`Start node: ${start.label}`, "edge");

  const heap = new MinHeap((a, b) => a.weight - b.weight);
  for (const nb of graph.neighbors(start.id)) heap.push(nb);

  let step = 0;
  while (visited.size < nodes.length && !heap.isEmpty()) {
    // Visual aid: highlight every edge currently crossing the cut, even
    // though the heap (not this scan) is what actually picks the winner.
    for (const e of edges) {
      const fromIn = visited.has(e.from);
      const toIn = visited.has(e.to);
      if ((fromIn && !toIn) || (!fromIn && toIn)) e.animating = true;
    }
    draw();
    await sleep(state.animSpeed / 2);
    edges.forEach((e) => (e.animating = false));

    // Pop the cheapest frontier edge; skip ones whose far end got
    // visited via a cheaper path already pushed earlier (lazy deletion).
    let next = heap.pop();
    while (next && visited.has(next.to)) next = heap.pop();
    if (!next) break; // heap exhausted — graph disconnected (caller checks first)

    const bestEdge = next.edgeRef;
    state.mstEdges.push(bestEdge);
    visited.add(next.to);

    for (const nb of graph.neighbors(next.to)) {
      if (!visited.has(nb.to)) heap.push(nb);
    }

    const n1 = nodes.find((n) => n.id === bestEdge.from);
    const n2 = nodes.find((n) => n.id === bestEdge.to);
    step++;
    log(`Step ${step}: Add edge ${n1.label}–${n2.label} (cost=${bestEdge.weight})`, "success");
    dom.resSteps.textContent = step;
    dom.progressFill.style.width = (visited.size / nodes.length) * 90 + "%";
    draw();
    await sleep(state.animSpeed);
  }
}
