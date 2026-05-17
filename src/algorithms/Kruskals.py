"""
╔══════════════════════════════════════════════════════════════════╗
║  Kruskals.py — Kruskal's MST Algorithm                           ║
╠══════════════════════════════════════════════════════════════════╣
║  TECHNIQUE : Greedy — Cycle Property of MSTs                     ║
║  DATA STRUC: Union-Find (DSU) + Sorted Edge List                 ║
║  TIME      : O(E log E)  [sort dominates]                        ║
║  SPACE     : O(V + E)                                            ║
╠══════════════════════════════════════════════════════════════════╣
║  CYCLE PROPERTY (why greedy is correct here):                    ║
║    The maximum-weight edge in any cycle is NEVER in any MST.     ║
║    Kruskal's skips exactly those edges via Union-Find.           ║
╠══════════════════════════════════════════════════════════════════╣
║  vs Prim's:                                                      ║
║    Kruskal's works on edges globally → better for sparse graphs  ║
║    Prim's grows one tree locally    → better for dense graphs    ║
╚══════════════════════════════════════════════════════════════════╝
"""

import time
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datastructures.Graph import Graph, Edge
from datastructures.UnionFind import UnionFind


class KruskalsAlgorithm:
    """
    Kruskal's Minimum Spanning Tree using Union-Find (DSU).

    ALGORITHM OVERVIEW
    ------------------
    1. Sort ALL edges by weight ascending.          [O(E log E)]
    2. Initialise Union-Find with all nodes.
    3. For each edge (u, v, w) in sorted order:
         a. If union(u, v) succeeds → different components → add to MST
         b. If union(u, v) fails   → same component → CYCLE, skip edge
    4. Stop when MST has V-1 edges (spanning tree complete).

    WHY UNION-FIND?
    ---------------
    Naive cycle check (DFS each time) : O(V) per edge → O(E·V) total
    Union-Find with optimisations      : O(α(V)) per edge → O(E) total
    Overall with sort                  : O(E log E)
    """

    def __init__(self, graph: Graph):
        self.graph      = graph
        self.mst_edges: list[Edge] = []
        self.mst_cost:  int        = 0
        self.steps:     list[str]  = []
        self.exec_time: float      = 0.0
        self.rejected:  int        = 0

    # ── Main Algorithm ────────────────────────────────────────────────

    def compute(self) -> list[Edge]:
        """
        Run Kruskal's MST.

        Returns
        -------
        list[Edge] — edges forming the MST
        """
        if not self.graph.is_connected():
            raise ValueError("Graph not connected — MST impossible.")

        nodes = self.graph.get_nodes()
        if not nodes:
            return []

        t0 = time.perf_counter()

        # Step 1 — Sort edges by weight
        sorted_edges = sorted(self.graph.edges, key=lambda e: e.weight)

        self._log("STEP 1: Sort all edges by cost")
        for e in sorted_edges:
            self._log(f"         S{e.src}─S{e.dest}  cost={e.weight}")
        self._log("─" * 52)
        self._log("STEP 2: Union-Find initialised for all nodes")
        self._log("STEP 3: Process edges greedily")
        self._log("─" * 52)

        # Step 2 — Initialise DSU
        uf = UnionFind(nodes)

        step = 0
        for e in sorted_edges:
            # Try to merge — returns False if same component (cycle)
            if uf.union(e.src, e.dest):
                self.mst_edges.append(e)
                self.mst_cost += e.weight
                step += 1
                self._log(
                    f"  Step {step:>2}: ACCEPT  S{e.src}─S{e.dest}  cost={e.weight:<6}"
                    f"  [MST cost: {self.mst_cost}]"
                )
                # V-1 edges → spanning tree is complete
                if len(self.mst_edges) == len(nodes) - 1:
                    break
            else:
                self.rejected += 1
                self._log(
                    f"         REJECT  S{e.src}─S{e.dest}  cost={e.weight:<6}"
                    f"  (would form a CYCLE)"
                )

        self.exec_time = (time.perf_counter() - t0) * 1_000
        self._log("─" * 52)
        self._log(f"DONE — MST cost = {self.mst_cost}  |  rejected {self.rejected} edges  "
                  f"|  time = {self.exec_time:.4f} ms")
        return self.mst_edges

    # ── Output ────────────────────────────────────────────────────────

    def _log(self, msg: str) -> None:
        self.steps.append(msg)

    def display_steps(self) -> None:
        print("\n  ┌─ Kruskal's Step-by-Step Trace ─────────────────┐")
        for line in self.steps:
            print(f"  │  {line}")
        print("  └────────────────────────────────────────────────┘")

    def display_result(self) -> None:
        sep = "═" * 52
        print(f"\n{sep}")
        print("  KRUSKAL'S ALGORITHM — RESULT")
        print(sep)
        print(f"  {'Edge':<20} {'Cost':>8}")
        print("  " + "─" * 30)
        for e in self.mst_edges:
            print(f"  S{e.src:>2} ────────── S{e.dest:<2}      {e.weight:>6}")
        print("  " + "─" * 30)
        print(f"  {'TOTAL MST COST':<20} {self.mst_cost:>8}")
        print(f"  {'MST EDGES':<20} {len(self.mst_edges):>8}")
        print(f"  {'EDGES REJECTED':<20} {self.rejected:>8}")
        print(f"  {'EXEC TIME (ms)':<20} {self.exec_time:>8.4f}")
        print(f"  {'COMPLEXITY':<20} {'O(E log E)':>10}")
        print(sep)


# ── Self-test ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    g = Graph()
    for s, d, w in [(1,2,4),(1,3,4),(2,3,2),(2,4,5),(3,4,5),(3,5,9),(4,5,7),(4,6,11),(5,6,7)]:
        g.add_edge(s, d, w)
    g.display()
    alg = KruskalsAlgorithm(g)
    alg.compute()
    alg.display_steps()
    alg.display_result()
