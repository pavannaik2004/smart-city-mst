"""
╔══════════════════════════════════════════════════════════════════╗
║  test_all.py — Full Test Suite                                   ║
╠══════════════════════════════════════════════════════════════════╣
║  Tests: Graph, UnionFind, MinHeap, Prim's, Kruskal's, BruteForce ║
║  Run:   python tests/test_all.py                                 ║
╚══════════════════════════════════════════════════════════════════╝
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from datastructures.Graph import Graph, Edge
from datastructures.UnionFind import UnionFind
from datastructures.MinHeap import MinHeap, HeapNode
from algorithms.Prims import PrimsAlgorithm
from algorithms.Kruskals import KruskalsAlgorithm
from algorithms.BruteForce import BruteForceAlgorithm

PASS = "  [PASS] ✓"
FAIL = "  [FAIL] ✗"
passed = 0
failed = 0


def check(label: str, condition: bool) -> None:
    global passed, failed
    if condition:
        print(f"{PASS}  {label}")
        passed += 1
    else:
        print(f"{FAIL}  {label}")
        failed += 1


def section(title: str) -> None:
    print(f"\n  ── {title} {'─'*(50-len(title))}")


# ─────────────────────────────────────────────────────────────────────
# GRAPH TESTS
# ─────────────────────────────────────────────────────────────────────
section("Graph — Basic Operations")

g = Graph()
g.add_edge(1, 2, 10)
g.add_edge(2, 3, 20)
g.add_edge(1, 3, 15)

check("add_edge: node count = 3",     g.node_count() == 3)
check("add_edge: edge count = 3",     g.edge_count() == 3)
check("duplicate edge rejected",      not g.add_edge(1, 2, 99))
check("edge count still 3",           g.edge_count() == 3)
check("get_edge_weight(1,2) = 10",    g.get_edge_weight(1, 2) == 10)
check("degree(2) = 2",                g.degree(2) == 2)
check("is_connected() = True",        g.is_connected())
check("total_weight = 45",            g.total_weight() == 45)

g2 = Graph()
g2.add_node(1)
g2.add_node(2)
check("disconnected graph",           not g2.is_connected())

section("Graph — Remove Operations")
g3 = Graph()
g3.add_edge(1, 2, 5)
g3.add_edge(2, 3, 8)
removed = g3.remove_edge(1, 2)
check("remove_edge returns True",     removed)
check("edge count after remove = 1",  g3.edge_count() == 1)
g3.remove_node(3)
check("node count after remove = 2",  g3.node_count() == 2)


# ─────────────────────────────────────────────────────────────────────
# UNION-FIND TESTS
# ─────────────────────────────────────────────────────────────────────
section("UnionFind — Correctness")

uf = UnionFind([1, 2, 3, 4, 5])
check("initial components = 5",       uf.component_count() == 5)
check("union(1,2) → True",            uf.union(1, 2))
check("union(3,4) → True",            uf.union(3, 4))
check("union(2,3) → True",            uf.union(2, 3))
check("union(1,4) → False (cycle)",   not uf.union(1, 4))
check("find(1) == find(4)",           uf.find(1) == uf.find(4))
check("components now = 2",           uf.component_count() == 2)

section("UnionFind — Path Compression")
uf2 = UnionFind([1, 2, 3, 4, 5, 6])
for a, b in [(1,2),(2,3),(3,4),(4,5),(5,6)]:
    uf2.union(a, b)
root_before = uf2.find(6)
_ = uf2.find(6)      # second call should be O(1) via compressed path
check("path compression: root stable", uf2.find(6) == root_before)
check("all in one component",          uf2.component_count() == 1)


# ─────────────────────────────────────────────────────────────────────
# MIN-HEAP TESTS
# ─────────────────────────────────────────────────────────────────────
section("MinHeap — Operations")

heap = MinHeap()
heap.insert(HeapNode(10, 1))
heap.insert(HeapNode(5,  2))
heap.insert(HeapNode(20, 3))
heap.insert(HeapNode(1,  4))

check("peek = key 1",                 heap.peek().key == 1)
check("extract_min = vertex 4",       heap.extract_min().vertex == 4)
check("extract_min = vertex 2",       heap.extract_min().vertex == 2)

heap2 = MinHeap()
for v, k in [(1,15),(2,30),(3,10),(4,25)]:
    heap2.insert(HeapNode(k, v))
heap2.decrease_key(2, 5)
check("decrease_key moves v2 to top", heap2.extract_min().vertex == 2)
heap2.decrease_key(99, 1)            # non-existent vertex
check("decrease_key on missing → ok", True)   # just shouldn't crash


# ─────────────────────────────────────────────────────────────────────
# ALGORITHM CORRECTNESS — KNOWN GRAPH
# ─────────────────────────────────────────────────────────────────────
section("Algorithms — Known MST Cost")

# Standard textbook graph, MST cost = 37
def build_test_graph() -> Graph:
    g = Graph()
    for s,d,w in [(1,2,4),(1,3,4),(2,3,2),(2,4,5),(3,4,5),(3,5,9),(4,5,7),(4,6,11),(5,6,7)]:
        g.add_edge(s, d, w)
    return g

g_test = build_test_graph()
p  = PrimsAlgorithm(g_test);    p.compute()
k  = KruskalsAlgorithm(g_test); k.compute()
bf = BruteForceAlgorithm(g_test); bf.compute()

check("Prim's MST cost = 25",         p.mst_cost  == 25)
check("Kruskal's MST cost = 25",      k.mst_cost  == 25)
check("BruteForce MST cost = 25",     bf.mst_cost == 25)
check("Prim's has V-1 = 5 edges",     len(p.mst_edges)  == 5)
check("Kruskal's has V-1 = 5 edges",  len(k.mst_edges)  == 5)
check("BruteForce has V-1 = 5 edges", len(bf.mst_edges) == 5)
check("All three costs agree",         p.mst_cost == k.mst_cost == bf.mst_cost)

section("Algorithms — City Network (8 nodes)")

g_city = Graph()
for s,d,w in [(1,2,15),(2,3,20),(1,4,12),(2,5,18),(3,5,14),(4,6,16),(4,5,30),(5,7,22),(6,7,10),(7,8,13),(5,8,25),(6,8,28),(3,8,35)]:
    g_city.add_edge(s, d, w)

pc  = PrimsAlgorithm(g_city);    pc.compute()
kc  = KruskalsAlgorithm(g_city); kc.compute()
bfc = BruteForceAlgorithm(g_city); bfc.compute()

check("City: all costs agree",        pc.mst_cost == kc.mst_cost == bfc.mst_cost)
check("City: MST has 7 edges",        len(pc.mst_edges) == 7)
check("City: MST cost > 0",           pc.mst_cost > 0)

section("Algorithms — Disconnected Graph")
g_dis = Graph()
g_dis.add_edge(1, 2, 5)
g_dis.add_node(3)   # isolated node

error_caught = False
try:
    PrimsAlgorithm(g_dis).compute()
except ValueError:
    error_caught = True
check("Prim's raises on disconnected graph",    error_caught)

error_caught = False
try:
    KruskalsAlgorithm(g_dis).compute()
except ValueError:
    error_caught = True
check("Kruskal's raises on disconnected graph", error_caught)


# ─────────────────────────────────────────────────────────────────────
# RANDOM GRAPH AGREEMENT
# ─────────────────────────────────────────────────────────────────────
section("Algorithms — Random Graph Agreement (10 trials)")

import random
from algorithms.ComplexityAnalyser import make_random_graph

random.seed(42)
all_agree = True
for trial in range(10):
    rg = make_random_graph(random.randint(4, 7), density=0.5, seed=trial)
    rp = PrimsAlgorithm(rg);    rp.compute()
    rk = KruskalsAlgorithm(rg); rk.compute()
    rb = BruteForceAlgorithm(rg); rb.compute()
    if not (rp.mst_cost == rk.mst_cost == rb.mst_cost):
        all_agree = False
        print(f"    MISMATCH on trial {trial+1}: "
              f"P={rp.mst_cost} K={rk.mst_cost} B={rb.mst_cost}")

check("All 10 random trials: P == K == B", all_agree)


# ─────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────
total = passed + failed
print(f"\n{'═'*52}")
print(f"  TEST SUMMARY:  {passed}/{total} passed   "
      f"({'ALL PASS ✓' if failed==0 else f'{failed} FAILED ✗'})")
print(f"{'═'*52}\n")
sys.exit(0 if failed == 0 else 1)
