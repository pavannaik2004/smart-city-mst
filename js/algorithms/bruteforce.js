/**
 * algorithms/bruteforce.js
 * ============================================================
 * Brute force baseline — what Prim's/Kruskal's greedy choices are
 * being compared against. Generates every combination of (V - 1)
 * edges out of E, keeps the ones that form a valid spanning tree,
 * and tracks the cheapest one seen.
 *
 * Data structure used:
 *   - UnionFind (datastructures/UnionFind.js) — same spanning-tree
 *     test Kruskal's uses: a candidate edge set is a spanning tree
 *     iff union-ing all its edges never reports "already connected"
 *     and every node ends up in one component.
 *
 * This is exhaustive search, not a heuristic: with C(E, V-1)
 * candidate subsets (each validated in O(V) via Union-Find) it is
 * only viable for small graphs — which is the point of showing it
 * next to two algorithms that scale to large ones. See
 * complexityAnalyzer.js#bruteForceComplexity for the live count.
 *
 *   Time:  O(C(E, V-1) · V)   (this implementation)
 *   Bound: O(V^V)              (textbook "try every labelled tree")
 *   Space: O(V²)
 * ============================================================
 */

import { state, dom, log } from "../app.js";
import { draw } from "../canvas.js";
import { UnionFind } from "../datastructures/UnionFind.js";

// Hard safety cap so a careless click on a 12-node random graph can't
// freeze the tab trying to enumerate C(E, V-1) subsets in the browser.
const MAX_ATTEMPTS = 200;

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** All k-element combinations of `arr`, C(n, k) total — the exhaustive search space. */
function generateSubsets(arr, k) {
  const result = [];
  function combo(start, current) {
    if (current.length === k) {
      result.push([...current]);
      return;
    }
    for (let i = start; i < arr.length; i++) {
      current.push(arr[i]);
      combo(i + 1, current);
      current.pop();
    }
  }
  combo(0, []);
  return result;
}

/** Is `subset` (exactly V-1 edges) a spanning tree of `nodes`? Validated via UnionFind. */
function isSpanningTree(nodes, subset) {
  if (subset.length !== nodes.length - 1) return false;
  const uf = new UnionFind(nodes.map((n) => n.id));
  for (const e of subset) {
    if (!uf.union(e.from, e.to)) return false; // would close a cycle -> not a tree
  }
  const root = uf.find(nodes[0].id);
  return nodes.every((n) => uf.find(n.id) === root);
}

export async function bruteForceMST() {
  log("=== BRUTE FORCE APPROACH ===", "info");
  log("Enumerate (V-1)-edge subsets, keep the cheapest spanning tree", "info");

  const { nodes, edges } = state;
  if (nodes.length > 8) {
    log("WARNING: Graph too large for exhaustive brute force!", "warn");
    log(`Capping search at ${MAX_ATTEMPTS} candidate subsets...`, "warn");
  }

  let bestCost = Infinity;
  let bestTree = [];
  let attempts = 0;

  const candidates = generateSubsets(edges, nodes.length - 1);
  log(`Total candidate subsets: C(E, V-1) = ${candidates.length}`, "edge");

  for (const subset of candidates) {
    attempts++;
    dom.resSteps.textContent = attempts;

    if (isSpanningTree(nodes, subset)) {
      const cost = subset.reduce((s, e) => s + e.weight, 0);
      if (cost < bestCost) {
        bestCost = cost;
        bestTree = subset;
        log(`New best tree found: cost=${cost}`, "success");
        state.mstEdges = [...bestTree];
        draw();
        await sleep(state.animSpeed / 2);
      }
    }

    if (attempts >= MAX_ATTEMPTS) {
      log(`Capped at ${MAX_ATTEMPTS} iterations (large graph)`, "warn");
      break;
    }
    await sleep(30);
  }

  state.mstEdges = bestTree;
}
