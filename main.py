"""
╔══════════════════════════════════════════════════════════════════╗
║        SMART CITY ROAD NETWORK PLANNER                           ║
║        main.py — Command-Line Entry Point                        ║
╠══════════════════════════════════════════════════════════════════╣
║  Usage:                                                          ║
║    python main.py               # full demo + benchmark          ║
║    python main.py --demo        # algorithm demo only            ║
║    python main.py --bench       # benchmark only                 ║
║    python main.py --theory      # complexity tables only         ║
║    python main.py --compare     # side-by-side comparison        ║
║    python main.py --custom      # enter your own graph           ║
╚══════════════════════════════════════════════════════════════════╝
"""

import sys, os, argparse, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from datastructures.Graph import Graph
from algorithms.Prims import PrimsAlgorithm
from algorithms.Kruskals import KruskalsAlgorithm
from algorithms.BruteForce import BruteForceAlgorithm
from algorithms.ComplexityAnalyser import (
    print_complexity_table, print_growth_table,
    run_benchmark, make_random_graph
)


# ── Preset Graphs ─────────────────────────────────────────────────────

def build_city_graph() -> Graph:
    """
    8-sensor Smart City network.
    Nodes represent intersection sensors, edges represent wiring routes.

         S1──15──S2──20──S3
         │        │       │
        12       18      14
         │        │       │
         S4──30──S5──22──S6
         │        │       │
        16       25      13
         │        │       │
         S7──10──S8──28──(back links)
    """
    g = Graph()
    for s, d, w in [
        (1, 2, 15), (2, 3, 20), (1, 4, 12), (2, 5, 18),
        (3, 5, 14), (4, 6, 16), (4, 5, 30), (5, 7, 22),
        (6, 7, 10), (7, 8, 13), (5, 8, 25), (6, 8, 28),
        (3, 8, 35),
    ]:
        g.add_edge(s, d, w)
    return g


def build_textbook_graph() -> Graph:
    """Classic 6-node MST textbook example. MST cost = 37."""
    g = Graph()
    for s, d, w in [
        (1, 2, 4), (1, 3, 4), (2, 3, 2), (2, 4, 5),
        (3, 4, 5), (3, 5, 9), (4, 5, 7), (4, 6, 11), (5, 6, 7),
    ]:
        g.add_edge(s, d, w)
    return g


# ── Banner ────────────────────────────────────────────────────────────

def print_banner() -> None:
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║      🌐  SMART CITY ROAD NETWORK PLANNER                         ║
║          Minimum Spanning Tree — Algorithm Suite                 ║
║                                                                  ║
║      Algorithms : Prim's  |  Kruskal's  |  Brute Force          ║
║      Techniques : Greedy (Cut / Cycle Property)                  ║
║      Data Strucs: Min-Heap  |  Union-Find  |  Adj. List         ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝""")


# ── Demo ──────────────────────────────────────────────────────────────

def run_demo() -> None:
    print("\n" + "█" * 64)
    print("  DEMO 1 — TEXTBOOK GRAPH (6 nodes, MST cost = 37)")
    print("█" * 64)
    g1 = build_textbook_graph()
    g1.display()
    g1.display_edge_list()
    _run_all_three(g1)

    print("\n" + "█" * 64)
    print("  DEMO 2 — SMART CITY NETWORK (8 sensors)")
    print("█" * 64)
    g2 = build_city_graph()
    g2.display()
    g2.display_edge_list()
    _run_all_three(g2)


def _run_all_three(g: Graph) -> None:
    """Run all three algorithms and print results + verification."""

    print("\n>>> PRIM'S ALGORITHM")
    p = PrimsAlgorithm(g)
    p.compute()
    p.display_steps()
    p.display_result()

    print("\n>>> KRUSKAL'S ALGORITHM")
    k = KruskalsAlgorithm(g)
    k.compute()
    k.display_steps()
    k.display_result()

    print("\n>>> BRUTE FORCE (exhaustive)")
    b = BruteForceAlgorithm(g)
    b.compute()
    b.display_steps()
    b.display_result()

    _verify(p, k, b)


def _verify(p, k, b) -> None:
    """Print verification table."""
    print("\n" + "─" * 52)
    print("  VERIFICATION — All algorithms must agree on MST cost")
    print("─" * 52)
    print(f"  {'Algorithm':<20} {'Cost':>8}  {'Edges':>6}  {'Time(ms)':>10}")
    print("  " + "─" * 48)
    for name, alg in [("Prim's", p), ("Kruskal's", k), ("Brute Force", b)]:
        print(f"  {name:<20} {alg.mst_cost:>8}  {len(alg.mst_edges):>6}  {alg.exec_time:>10.4f}")
    agree = p.mst_cost == k.mst_cost == b.mst_cost
    print(f"\n  All costs agree: {'✓ YES — greedy correctness confirmed!' if agree else '✗ NO!'}")
    print("─" * 52)


# ── Side-by-Side Comparison ───────────────────────────────────────────

def run_comparison() -> None:
    print("\n" + "═" * 64)
    print("  SIDE-BY-SIDE COMPARISON — Random Graphs (5 trials)")
    print("═" * 64)
    random.seed(7)

    for trial in range(1, 6):
        n = random.randint(5, 7)
        g = make_random_graph(n, density=0.55, seed=trial * 13)
        print(f"\n  Trial {trial}: {n} nodes, {g.edge_count()} edges")

        p = PrimsAlgorithm(g);    p.compute()
        k = KruskalsAlgorithm(g); k.compute()
        b = BruteForceAlgorithm(g); b.compute()

        print(f"    Prim's     cost={p.mst_cost:<6}  time={p.exec_time:.4f} ms")
        print(f"    Kruskal's  cost={k.mst_cost:<6}  time={k.exec_time:.4f} ms")
        print(f"    BruteForce cost={b.mst_cost:<6}  time={b.exec_time:.4f} ms")
        status = "✓ MATCH" if p.mst_cost == k.mst_cost == b.mst_cost else "✗ MISMATCH"
        print(f"    Status: {status}")


# ── Custom Graph Input ────────────────────────────────────────────────

def run_custom() -> None:
    print("\n  CUSTOM GRAPH INPUT")
    print("  Enter edges as: from to weight  (e.g. 1 2 15)")
    print("  Type 'done' when finished.\n")

    g = Graph()
    while True:
        line = input("  Edge> ").strip()
        if line.lower() in ("done", "d", ""):
            break
        parts = line.split()
        if len(parts) != 3:
            print("  → Format: <from> <to> <weight>"); continue
        try:
            s, d, w = int(parts[0]), int(parts[1]), int(parts[2])
            if g.add_edge(s, d, w):
                print(f"  → Added S{s}─S{d} (cost={w})")
            else:
                print("  → Edge already exists")
        except ValueError:
            print("  → Invalid input (use integers)")

    if g.edge_count() == 0:
        print("  No edges entered."); return
    if not g.is_connected():
        print("  ⚠ Graph is not connected — MST not possible."); return

    g.display()
    g.display_edge_list()
    _run_all_three(g)


# ── CLI ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Smart City MST Planner — CLI",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--demo",    action="store_true", help="Run algorithm demo")
    parser.add_argument("--bench",   action="store_true", help="Run empirical benchmark")
    parser.add_argument("--theory",  action="store_true", help="Print complexity tables")
    parser.add_argument("--compare", action="store_true", help="Side-by-side comparison")
    parser.add_argument("--custom",  action="store_true", help="Enter your own graph")
    args = parser.parse_args()

    print_banner()
    run_all = not any([args.demo, args.bench, args.theory, args.compare, args.custom])

    if args.theory  or run_all: print_complexity_table(); print_growth_table()
    if args.demo    or run_all: run_demo()
    if args.compare or run_all: run_comparison()
    if args.bench   or run_all: run_benchmark()
    if args.custom:             run_custom()


if __name__ == "__main__":
    main()
