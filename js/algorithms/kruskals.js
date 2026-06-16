/**
 * algorithms/kruskals.js
 * ============================================================
 * Kruskal's algorithm — sorts every edge by weight, then walks
 * them cheapest-first, accepting an edge unless it would join two
 * nodes already in the same component (i.e. would close a cycle).
 * Correctness comes from the Cycle Property: the priciest edge on
 * any cycle is never needed in an MST.
 *
 * Data structure used:
 *   - UnionFind (datastructures/UnionFind.js) — O(log V) worst case,
 *     ~O(1) amortised find/union, answering "same component?" without
 *     a graph traversal per edge.
 *
 * Sorting the E edges dominates the runtime:
 *   Time:  O(E log E)
 *   Space: O(V + E)
 * ============================================================
 */

import { state, dom, log } from "../app.js";
import { draw } from "../canvas.js";
import { UnionFind } from "../datastructures/UnionFind.js";

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function kruskalMST() {
  log("=== KRUSKAL'S ALGORITHM ===", "info");
  log("Data Structure: Union-Find (Disjoint Set)", "info");
  log("Complexity: O(E log E)", "info");
  log("", "");

  const { nodes, edges } = state;
  const uf = new UnionFind(nodes.map((n) => n.id));

  const sorted = [...edges].sort((a, b) => a.weight - b.weight);
  log(`Sorted ${sorted.length} edges by cost`, "edge");
  sorted.forEach((e) => {
    const n1 = nodes.find((n) => n.id === e.from);
    const n2 = nodes.find((n) => n.id === e.to);
    log(`  Edge ${n1.label}–${n2.label}: ${e.weight}`, "edge");
  });

  let step = 0;
  for (const e of sorted) {
    const n1 = nodes.find((n) => n.id === e.from);
    const n2 = nodes.find((n) => n.id === e.to);
    e.animating = true;
    draw();
    await sleep(state.animSpeed / 2);
    e.animating = false;

    if (uf.union(e.from, e.to)) {
      state.mstEdges.push(e);
      step++;
      log(`Step ${step}: Accept ${n1.label}–${n2.label} (cost=${e.weight}) ✓`, "success");
      dom.resSteps.textContent = step;
      dom.progressFill.style.width = (step / (nodes.length - 1)) * 90 + "%";
      draw();
      await sleep(state.animSpeed);
      if (state.mstEdges.length === nodes.length - 1) break; // tree complete
    } else {
      log(`Reject ${n1.label}–${n2.label} (forms cycle)`, "warn");
      draw();
      await sleep(state.animSpeed / 2);
    }
  }
}
