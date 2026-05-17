"""
╔══════════════════════════════════════════════════════════════════╗
║  Prims.py — Prim's MST Algorithm                                 ║
╠══════════════════════════════════════════════════════════════════╣
║  TECHNIQUE : Greedy — Cut Property of MSTs                       ║
║  DATA STRUC: Binary Min-Heap + Adjacency List                    ║
║  TIME      : O(E log V)                                          ║
║  SPACE     : O(V + E)                                            ║
╠══════════════════════════════════════════════════════════════════╣
║  CUT PROPERTY (why greedy is correct here):                      ║
║    For any cut (S, V-S) of the graph, the minimum weight edge    ║
║    crossing the cut MUST be in every MST.                        ║
║    Prim's always picks this edge → always safe.                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

import time
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datastructures.Graph import Graph, Edge
from datastructures.MinHeap import MinHeap, HeapNode


class PrimsAlgorithm:
    """
    Prim's Minimum Spanning Tree using a Binary Min-Heap.

    ALGORITHM OVERVIEW
    ------------------
    1. Start from any node (default: node 1).
    2. Initialise all node keys to ∞, start node key to 0.
    3. Load all nodes into min-heap.
    4. While heap is not empty:
         a. Extract node u with minimum key (cheapest crossing edge).
         b. Mark u as in-MST.
         c. For each neighbour v of u:
              - If v not in MST and edge(u,v) < key[v]:
                  → Update key[v] = edge weight
                  → Update parent[v] = u
                  → decrease_key in heap
    5. Collect MST edges via parent[] array.

    WHY MIN-HEAP?
    -------------
    Naive scan for minimum: O(V) per step × V steps = O(V²)
    With min-heap: O(log V) per extraction × E relaxations = O(E log V)
    """

    def __init__(self, graph: Graph):
        self.graph     = graph
        self.mst_edges: list[Edge] = []
        self.mst_cost:  int        = 0
        self.steps:     list[str]  = []
        self.exec_time: float      = 0.0
        self.step_count: int       = 0

    # ── Main Algorithm ────────────────────────────────────────────────

    def compute(self, start: int = None) -> list[Edge]:
        """
        Run Prim's MST.

        Parameters
        ----------
        start : starting sensor node (default = first node)

        Returns
        -------
        list[Edge] — edges forming the MST
        """
        if not self.graph.is_connected():
            raise ValueError("Graph not connected — MST impossible.")

        nodes = self.graph.get_nodes()
        if not nodes:
            return []
        if start is None:
            start = nodes[0]

        t0 = time.perf_counter()

        INF = float('inf')
        key    = {v: INF   for v in nodes}   # cheapest edge weight to reach v
        parent = {v: None  for v in nodes}   # which node connects to v in MST
        in_mst = {v: False for v in nodes}   # is v already in MST?
        key[start] = 0

        # Load all nodes into the min-heap with their initial keys
        heap = MinHeap()
        for v in nodes:
            heap.insert(HeapNode(key[v], v))

        self._log("INITIALISATION")
        self._log(f"  Start node : S{start}")
        self._log(f"  All keys   : ∞ except key[S{start}] = 0")
        self._log("─" * 52)
        self._log("MAIN LOOP")

        while not heap.is_empty():
            hn = heap.extract_min()
            u  = hn.vertex

            # Skip if already processed (stale entry)
            if in_mst[u]:
                continue
            in_mst[u] = True

            if parent[u] is not None:
                edge = Edge(parent[u], u, key[u])
                self.mst_edges.append(edge)
                self.mst_cost += key[u]
                self.step_count += 1
                self._log(
                    f"  Step {self.step_count:>2}: Extract S{u} "
                    f"→ Add edge S{parent[u]}─S{u} (cost={key[u]})  "
                    f"[MST cost so far: {self.mst_cost}]"
                )
            else:
                self._log(f"  Step  0: Extract S{u} (start, no edge added)")

            # Relax all neighbours of u
            for v, weight in self.graph.adj[u]:
                if not in_mst[v] and weight < key[v]:
                    old = key[v]
                    key[v]    = weight
                    parent[v] = u
                    heap.decrease_key(v, weight)
                    heap.update_data(v, u)
                    self._log(
                        f"           Relax S{u}→S{v}: "
                        f"key {old if old<float('inf') else '∞'} → {weight}  "
                        f"parent[S{v}]=S{u}"
                    )

        self.exec_time = (time.perf_counter() - t0) * 1_000
        self._log("─" * 52)
        self._log(f"DONE — MST cost = {self.mst_cost}  |  time = {self.exec_time:.4f} ms")
        return self.mst_edges

    # ── Output ────────────────────────────────────────────────────────

    def _log(self, msg: str) -> None:
        self.steps.append(msg)

    def display_steps(self) -> None:
        print("\n  ┌─ Prim's Step-by-Step Trace ────────────────────┐")
        for line in self.steps:
            print(f"  │  {line}")
        print("  └────────────────────────────────────────────────┘")

    def display_result(self) -> None:
        sep = "═" * 52
        print(f"\n{sep}")
        print("  PRIM'S ALGORITHM — RESULT")
        print(sep)
        print(f"  {'Edge':<20} {'Cost':>8}")
        print("  " + "─" * 30)
        for e in self.mst_edges:
            print(f"  S{e.src:>2} ────────── S{e.dest:<2}      {e.weight:>6}")
        print("  " + "─" * 30)
        print(f"  {'TOTAL MST COST':<20} {self.mst_cost:>8}")
        print(f"  {'MST EDGES':<20} {len(self.mst_edges):>8}")
        print(f"  {'EXEC TIME (ms)':<20} {self.exec_time:>8.4f}")
        print(f"  {'COMPLEXITY':<20} {'O(E log V)':>10}")
        print(sep)


# ── Self-test ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    g = Graph()
    for s, d, w in [(1,2,4),(1,3,4),(2,3,2),(2,4,5),(3,4,5),(3,5,9),(4,5,7),(4,6,11),(5,6,7)]:
        g.add_edge(s, d, w)
    g.display()
    alg = PrimsAlgorithm(g)
    alg.compute(start=1)
    alg.display_steps()
    alg.display_result()
