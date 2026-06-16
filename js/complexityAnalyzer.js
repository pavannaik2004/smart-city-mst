/**
 * complexityAnalyzer.js
 * ============================================================
 * Static (theoretical) complexity analysis — the "calculate time
 * complexity" half of the toolkit. Given the current graph size
 * (V nodes, E edges), these functions derive each algorithm's
 * Big-O time/space class *and* a concrete estimated operation
 * count by substituting V and E into that formula, and render
 * that into the "Complexity Analysis" panel.
 *
 * timeAnalyzer.js is the other half: it measures what the
 * browser actually clocked for a run, so the two can be compared.
 * ============================================================
 */

import { dom } from "./app.js";

/** log base 2 — the natural base for heap/merge-sort operation counts. */
function log2(x) {
  return Math.log(Math.max(1, x)) / Math.LN2;
}

/** C(n, k), computed iteratively (no factorials) to stay numerically stable for larger n. */
function binomial(n, k) {
  if (k < 0 || k > n) return 0;
  let result = 1;
  for (let i = 0; i < k; i++) result = (result * (n - i)) / (i + 1);
  return result;
}

/**
 * Prim's algorithm (MinHeap + Graph implementation, see algorithms/prims.js):
 * every node added to the tree pulls from a heap of at most E pending
 * edges, and may push up to deg(node) new ones — O(E) heap operations
 * total, each O(log V).
 *   Time:  O((V + E) log V)
 *   Space: O(V + E)   — adjacency list + heap
 */
export function primComplexity(V, E) {
  const ops = (V + E) * log2(V);
  return { formula: "O((V + E) log V)", space: "O(V + E)", ops };
}

/**
 * Kruskal's algorithm (sort + UnionFind, see algorithms/kruskals.js):
 * sorting the E edges once dominates; the E subsequent find/union calls
 * are near O(1) amortised (path compression + union by rank).
 *   Time:  O(E log E)
 *   Space: O(V + E)
 */
export function kruskalComplexity(V, E) {
  const ops = E * log2(E) + E; // sort + E find/union calls
  return { formula: "O(E log E)", space: "O(V + E)", ops };
}

/**
 * Brute force (see algorithms/bruteforce.js): enumerates every
 * combination of (V - 1) edges out of E and validates each with a
 * UnionFind pass (O(V)). The number of (V-1)-combinations is
 * C(E, V-1) — the *real* cost of this implementation, tighter than
 * the textbook "try every labelled tree on V nodes" bound of O(V^V)
 * shown alongside it for reference.
 *   Time:  O(C(E, V-1) · V)     (this implementation)
 *   Bound: O(V^V)                (textbook worst case)
 *   Space: O(V²)
 */
export function bruteForceComplexity(V, E) {
  const k = Math.max(0, V - 1);
  const combos = binomial(E, k);
  const ops = combos * V;
  return { formula: "O(C(E,V-1) · V)", textbookBound: "O(Vᵛ)", space: "O(V²)", ops, combos };
}

/** Computes all three estimates at once for a given graph size. */
export function computeAllComplexities(V, E) {
  return {
    prim: primComplexity(V, E),
    kruskal: kruskalComplexity(V, E),
    brute: bruteForceComplexity(V, E),
  };
}

/** Formats a (possibly huge) operation count compactly, e.g. 12400 -> "12.4K". */
export function formatOps(n) {
  if (!isFinite(n)) return "∞";
  if (n < 1000) return Math.round(n).toString();
  if (n < 1e6) return (n / 1e3).toFixed(1) + "K";
  if (n < 1e9) return (n / 1e6).toFixed(1) + "M";
  return n.toExponential(2);
}

/**
 * Recomputes every estimate for the given graph size and re-renders the
 * "Complexity Analysis" panel with live numbers. Called from app.js
 * whenever the graph changes, so the panel always matches the canvas.
 */
export function renderComplexityPanel(V, E) {
  const { prim, kruskal, brute } = computeAllComplexities(V, E);

  dom.complexityBody.innerHTML = `
    <div class="complexity-item">
      <span class="algo-name">Prim's</span>
      <span class="time-val">${prim.formula}</span>
      <span class="space-val">${prim.space}</span>
    </div>
    <div class="complexity-item">
      <span class="algo-name">Kruskal's</span>
      <span class="time-val">${kruskal.formula}</span>
      <span class="space-val">${kruskal.space}</span>
    </div>
    <div class="complexity-item">
      <span class="algo-name">Brute Force</span>
      <span class="time-val">${brute.formula}</span>
      <span class="space-val">${brute.space}</span>
    </div>
    <div class="complexity-note">
      For V=${V}, E=${E} — estimated basic operations:<br>
      <b>Prim's</b> ~${formatOps(prim.ops)} &nbsp;
      <b>Kruskal's</b> ~${formatOps(kruskal.ops)} &nbsp;
      <b>Brute</b> ~${formatOps(brute.ops)} (${formatOps(brute.combos)} subsets checked;
      textbook bound ${brute.textbookBound})
    </div>
  `;
}
