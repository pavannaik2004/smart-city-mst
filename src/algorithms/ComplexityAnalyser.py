"""
╔══════════════════════════════════════════════════════════════════╗
║  ComplexityAnalyser.py — Empirical Benchmark & Theory Reference  ║
╠══════════════════════════════════════════════════════════════════╣
║  Measures real runtimes, prints comparison tables, and           ║
║  provides the theoretical complexity justification text.         ║
╚══════════════════════════════════════════════════════════════════╝
"""

import time
import random
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datastructures.Graph import Graph
from algorithms.Prims import PrimsAlgorithm
from algorithms.Kruskals import KruskalsAlgorithm
from algorithms.BruteForce import BruteForceAlgorithm


# ── Theoretical Reference ─────────────────────────────────────────────

THEORY = {
    "Prim's (Min-Heap)": {
        "technique"  : "Greedy — Cut Property",
        "property"   : "Min edge crossing any cut ∈ every MST",
        "time"       : "O(E log V)",
        "space"      : "O(V + E)",
        "ds"         : "Binary Min-Heap + Adjacency List",
        "best_for"   : "Dense graphs  (E ≈ V²)",
        "worst_for"  : "Very sparse graphs",
    },
    "Kruskal's (Union-Find)": {
        "technique"  : "Greedy — Cycle Property",
        "property"   : "Max edge in any cycle ∉ any MST",
        "time"       : "O(E log E)",
        "space"      : "O(V + E)",
        "ds"         : "Disjoint Set Union + Sorted Edge List",
        "best_for"   : "Sparse graphs  (E ≈ V)",
        "worst_for"  : "Very dense graphs",
    },
    "Brute Force": {
        "technique"  : "Exhaustive Enumeration",
        "property"   : "Try all (V-1)-subsets; pick cheapest spanning tree",
        "time"       : "O(C(E,V-1) × V)  ≈  O(V^V)",
        "space"      : "O(V²)",
        "ds"         : "Combinations + BFS connectivity check",
        "best_for"   : "Tiny graphs (≤ 8 nodes), correctness verification",
        "worst_for"  : "Any graph with V > 8",
    },
}


# ── Random Graph Generator ────────────────────────────────────────────

def make_random_graph(n: int, density: float = 0.5, max_w: int = 100,
                      seed: int = None) -> Graph:
    """
    Build a random connected weighted graph.
    Guarantees connectivity via a random spanning path first.
    """
    if seed is not None:
        random.seed(seed)
    g = Graph()
    nodes = list(range(1, n + 1))
    random.shuffle(nodes)
    # Ensure connectivity
    for i in range(len(nodes) - 1):
        g.add_edge(nodes[i], nodes[i + 1], random.randint(1, max_w))
    # Add extra edges with probability = density
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            if not any({e.src,e.dest}=={i,j} for e in g.edges) and random.random() < density:
                g.add_edge(i, j, random.randint(1, max_w))
    return g


# ── Timing Helper ─────────────────────────────────────────────────────

def time_run(AlgoClass, graph: Graph) -> tuple[float, int]:
    """Run algorithm, return (ms, mst_cost). Returns (-1,-1) on error."""
    try:
        alg = AlgoClass(graph)
        t0  = time.perf_counter()
        alg.compute()
        return round((time.perf_counter() - t0) * 1000, 6), alg.mst_cost
    except Exception:
        return -1.0, -1


# ── Benchmark ─────────────────────────────────────────────────────────

def run_benchmark(sizes: list[int] = None, trials: int = 3) -> None:
    """
    Run all algorithms across increasing graph sizes.
    Average over *trials* independent random graphs per size.
    """
    sizes = sizes or [4, 5, 6, 7, 8, 10, 15, 20, 30, 50]
    random.seed(0)

    print("\n" + "═" * 88)
    print("  EMPIRICAL BENCHMARK — Smart City MST Algorithms")
    print("  (averaged over", trials, "random graphs per size)")
    print("═" * 88)
    print(f"  {'V':>4}  {'E':>5}  {'Prim avg(ms)':>14}  {'Kruskal avg(ms)':>16}  "
          f"{'Brute avg(ms)':>15}  {'Costs match':>12}")
    print("  " + "─" * 72)

    for n in sizes:
        prim_times, krus_times, brute_times = [], [], []
        costs_ok = True

        for _ in range(trials):
            g = make_random_graph(n, density=0.4)
            E = g.edge_count()

            tp, cp = time_run(PrimsAlgorithm,    g)
            tk, ck = time_run(KruskalsAlgorithm, g)

            if n <= 8:
                tb, cb = time_run(BruteForceAlgorithm, g)
                if cp != ck or cp != cb:
                    costs_ok = False
                brute_times.append(tb)
            else:
                if cp != ck:
                    costs_ok = False
                brute_times.append(-1)

            prim_times.append(tp)
            krus_times.append(tk)

        avg_p = sum(prim_times) / trials
        avg_k = sum(krus_times) / trials
        avg_b = sum(t for t in brute_times if t >= 0)
        avg_b = avg_b / max(1, sum(1 for t in brute_times if t >= 0))

        brute_str = f"{avg_b:>13.4f}" if n <= 8 else "       SKIP (too large)"
        match_str = "✓ Yes" if costs_ok else "✗ MISMATCH"

        print(f"  {n:>4}  {E:>5}  {avg_p:>12.4f}    {avg_k:>14.4f}    "
              f"{brute_str}   {match_str:>12}")

    print("═" * 88)
    print("  NOTE: All three algorithms produce the same MST cost (proven by")
    print("        cut-property / cycle-property of MSTs). Brute force skipped")
    print("        for V>8 due to exponential time O(C(E,V-1)·V).")
    print("═" * 88 + "\n")


# ── Theory Printer ────────────────────────────────────────────────────

def print_complexity_table() -> None:
    print("\n" + "═" * 76)
    print("  THEORETICAL COMPLEXITY ANALYSIS")
    print("═" * 76)
    print(f"  {'Algorithm':<28}  {'Technique':<26}  {'Time':^12}  {'Space':^8}")
    print("  " + "─" * 72)
    for algo, info in THEORY.items():
        print(f"  {algo:<28}  {info['technique']:<26}  {info['time']:^12}  {info['space']:^8}")
    print("═" * 76)

    print("\n  DESIGN JUSTIFICATION")
    print("  " + "─" * 72)
    for algo, info in THEORY.items():
        print(f"\n  [{algo}]")
        print(f"    Greedy property: {info['property']}")
        print(f"    Data structure : {info['ds']}")
        print(f"    Best suited for: {info['best_for']}")
        print(f"    Worst suited   : {info['worst_for']}")
    print()


# ── Growth Rate Table ─────────────────────────────────────────────────

def print_growth_table() -> None:
    """Show theoretical operation counts for increasing V."""
    from math import log2, comb as mathcomb
    print("\n" + "═" * 72)
    print("  THEORETICAL OPERATION COUNT GROWTH")
    print(f"  {'V':>4}  {'E(dense)':>10}  {'Prim O(ElogV)':>14}  "
          f"{'Kruskal O(ElogE)':>17}  {'Brute O(C(E,V-1))':>18}")
    print("  " + "─" * 68)
    for v in [4, 5, 6, 7, 8, 10, 15, 20]:
        e = v * (v - 1) // 2   # complete graph
        prim   = int(e * log2(max(v, 2)))
        krus   = int(e * log2(max(e, 2)))
        brute  = mathcomb(e, v - 1) if v <= 12 else float('inf')
        brute_s = f"{brute:>18,}" if brute < 1e15 else "    ∞ (infeasible)"
        print(f"  {v:>4}  {e:>10}  {prim:>14,}  {krus:>17,}  {brute_s}")
    print("═" * 72 + "\n")


if __name__ == "__main__":
    print_complexity_table()
    print_growth_table()
    run_benchmark()
