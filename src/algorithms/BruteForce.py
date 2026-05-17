"""
╔══════════════════════════════════════════════════════════════════╗
║  BruteForce.py — Exhaustive MST Finder                           ║
╠══════════════════════════════════════════════════════════════════╣
║  TECHNIQUE : Exhaustive Enumeration of all spanning trees        ║
║  DATA STRUC: Combinations + Union-Find cycle check               ║
║  TIME      : O(C(E, V-1) × α(V))  ≈  O(V^V) worst case         ║
║  SPACE     : O(V + E)                                            ║
╠══════════════════════════════════════════════════════════════════╣
║  OPTIMISATIONS (makes graphs up to ~13 nodes feasible):          ║
║    1. Sort edges by weight → cost pruning (skip if cost≥best)    ║
║    2. Union-Find cycle check O(α(V)) instead of BFS O(V+E)       ║
║    3. 30-second time limit with graceful early exit              ║
║  PURPOSE : Correctness baseline & demonstration of exponential   ║
║            growth — shows exactly WHY greedy algorithms exist.   ║
╚══════════════════════════════════════════════════════════════════╝
"""

import time
import sys, os
from itertools import combinations
from math import comb
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datastructures.Graph import Graph, Edge
from datastructures.UnionFind import UnionFind

TIME_LIMIT_SEC = 30.0   # stop after this many seconds


class BruteForceAlgorithm:
    """
    Brute-force MST by enumerating ALL C(E, V-1) subsets of edges.

    ALGORITHM OVERVIEW
    ------------------
    1. Sort all edges by weight (enables cost-bound pruning).
    2. Generate every (V-1)-subset of edges.
    3. For each subset:
         a. Compute total cost — PRUNE if >= best cost found so far.
         b. Check spanning-tree property via Union-Find:
              - No cycle  → union() returns False when src & dest
                            already in same component.
              - Connected → guaranteed by V-1 edges + no cycle.
    4. Return the minimum-cost valid spanning tree.

    COST PRUNING EXPLANATION
    ------------------------
    Since edges are sorted ascending by weight, any subset produced by
    combinations() has a predictable lower bound.  If the subset sum
    already meets or exceeds the current best, we skip it immediately
    without even running the Union-Find check — this is branch-and-bound
    and dramatically reduces work for denser graphs.

    EXPONENTIAL GROWTH (why greedy matters)
    ----------------------------------------
    V= 8, E=28  →  C(28, 7) =       1,184,040  subsets
    V=10, E=45  →  C(45, 9) =     886,163,135  subsets  ← too slow
    V=13, E=21  →  C(21,12) =         293,930  subsets  ← fast (sparse!)
    V=13, E=78  →  C(78,12) = 43,430,966,148,115  ← impossible

    Key insight: feasibility depends on EDGE count, not just node count.
    Sparse 13-node graphs are fine; dense ones are not.
    """

    def __init__(self, graph: Graph):
        self.graph          = graph
        self.mst_edges:     list[Edge] = []
        self.mst_cost:      int        = 0
        self.steps:         list[str]  = []
        self.exec_time:     float      = 0.0
        self.total_checked: int        = 0
        self.total_valid:   int        = 0
        self.timed_out:     bool       = False
        self.result_exact:  bool       = True

    # ── Main Algorithm ────────────────────────────────────────────────

    def compute(self) -> list[Edge]:
        """
        Enumerate all spanning-tree subsets, return the cheapest.

        Returns
        -------
        list[Edge] — MST edges (exact unless time limit hit)
        """
        if not self.graph.is_connected():
            raise ValueError("Graph not connected — MST impossible.")

        nodes     = self.graph.get_nodes()
        V         = len(nodes)
        k         = V - 1

        # Sort edges ascending — enables cost pruning
        all_edges = sorted(self.graph.get_edges(), key=lambda e: e.weight)
        E         = len(all_edges)

        if E < k:
            raise ValueError("Not enough edges to span all nodes.")

        total_combos = comb(E, k)

        self._log(f"Nodes  : {V}   Edges : {E}   Need : {k} edges in MST")
        self._log(f"C({E},{k}) = {total_combos:,} total subsets")
        self._log(f"Time limit : {TIME_LIMIT_SEC}s")
        self._log("─" * 58)
        self._log("Sorted edge list (ascending weight):")
        for i, e in enumerate(all_edges, 1):
            self._log(f"  [{i:>2}] S{e.src}─S{e.dest}  weight={e.weight}")
        self._log("─" * 58)

        best_cost   = float('inf')
        best_subset: list[Edge] = []
        t0 = time.perf_counter()

        for subset in combinations(all_edges, k):
            # Time-limit guard — check every 4096 iterations
            if (self.total_checked & 0xFFF) == 0:
                if time.perf_counter() - t0 > TIME_LIMIT_SEC:
                    self.timed_out    = True
                    self.result_exact = False
                    self._log(f"⏱ TIME LIMIT {TIME_LIMIT_SEC}s reached — stopping early")
                    break

            self.total_checked += 1

            # PRUNING: skip if subset total cost can't beat best
            subset_cost = sum(e.weight for e in subset)
            if subset_cost >= best_cost:
                continue

            # SPANNING TREE CHECK via Union-Find
            if self._is_spanning_tree_uf(list(subset), nodes):
                self.total_valid += 1
                edges_str = "  ".join(
                    f"S{e.src}-S{e.dest}({e.weight})" for e in subset
                )
                if subset_cost < best_cost:
                    best_cost   = subset_cost
                    best_subset = list(subset)
                    self._log(f"✓ NEW BEST  cost={subset_cost:<6}  [{edges_str}]")

        self.mst_edges  = best_subset
        self.mst_cost   = int(best_cost) if best_cost < float('inf') else 0
        self.exec_time  = (time.perf_counter() - t0) * 1_000

        self._log("─" * 58)
        self._log(f"Subsets checked   : {self.total_checked:,}")
        self._log(f"Valid span. trees  : {self.total_valid:,}")
        self._log(f"Pruned (skipped)  : {self.total_checked - self.total_valid:,}")
        self._log(f"Exact result      : {'Yes ✓' if self.result_exact else 'No — timed out ⏱'}")
        self._log(f"MST cost          : {self.mst_cost}")
        self._log(f"Execution time    : {self.exec_time:.4f} ms")
        return self.mst_edges

    # ── Spanning Tree Check — Union-Find ──────────────────────────────

    def _is_spanning_tree_uf(self, subset: list[Edge], nodes: list[int]) -> bool:
        """
        Validate spanning tree using Union-Find.

        V-1 edges with no cycle → connected spanning tree (by theorem).
        Union-Find detects cycles in O(α(V)) per edge — much faster
        than the BFS approach which costs O(V + E) per check.

        Time per call: O((V-1) · α(V))  ≈  O(V)
        """
        uf = UnionFind(nodes)
        for e in subset:
            if not uf.union(e.src, e.dest):
                return False   # cycle → not a tree
        return uf.component_count() == 1

    # ── Helpers ───────────────────────────────────────────────────────

    def _log(self, msg: str) -> None:
        self.steps.append(msg)

    # ── Output ────────────────────────────────────────────────────────

    def display_steps(self) -> None:
        print("\n  ┌─ Brute Force Step-by-Step Trace ───────────────┐")
        for line in self.steps:
            print(f"  │  {line}")
        print("  └────────────────────────────────────────────────┘")

    def display_result(self) -> None:
        sep = "═" * 52
        print(f"\n{sep}")
        print("  BRUTE FORCE — MST RESULT")
        print(sep)
        print(f"  {'Subsets Checked':<24} {self.total_checked:>12,}")
        print(f"  {'Valid Spanning Trees':<24} {self.total_valid:>12,}")
        print(f"  {'Result Exact':<24} {'Yes ✓' if self.result_exact else 'No (timed out)':>12}")
        print("  " + "─" * 38)
        print(f"  {'Edge':<20} {'Cost':>8}")
        print("  " + "─" * 30)
        for e in self.mst_edges:
            print(f"  S{e.src:>2} ────────── S{e.dest:<2}      {e.weight:>6}")
        print("  " + "─" * 30)
        print(f"  {'TOTAL MST COST':<24} {self.mst_cost:>12}")
        print(f"  {'MST EDGES':<24} {len(self.mst_edges):>12}")
        print(f"  {'EXEC TIME (ms)':<24} {self.exec_time:>12.4f}")
        print(f"  {'COMPLEXITY':<24} {'O(C(E,V-1)·α(V))':>12}")
        print(sep)


# ── Self-test ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Test 1: Small graph (6 nodes) ===")
    g = Graph()
    for s, d, w in [(1,2,4),(1,3,4),(2,3,2),(2,4,5),(3,4,5),
                    (3,5,9),(4,5,7),(4,6,11),(5,6,7)]:
        g.add_edge(s, d, w)
    g.display()
    alg = BruteForceAlgorithm(g)
    alg.compute()
    alg.display_steps()
    alg.display_result()

    print("\n=== Test 2: City graph (13 nodes, 21 edges) ===")
    g2 = Graph()
    for s,d,w in [(1,2,15),(2,3,20),(1,4,12),(2,5,18),(3,5,14),
                  (4,6,16),(4,5,30),(5,7,22),(6,7,10),(7,8,13),
                  (5,8,25),(6,8,28),(3,8,35),(8,9,8),(9,10,11),
                  (10,11,17),(11,12,9),(12,13,14),(9,13,22),
                  (10,13,19),(11,13,6)]:
        g2.add_edge(s, d, w)
    alg2 = BruteForceAlgorithm(g2)
    alg2.compute()
    alg2.display_result()
    print(f"Result exact: {alg2.result_exact}")
