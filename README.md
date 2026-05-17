# Smart City Road Network Planner
## Minimum Spanning Tree — Algorithm Suite

### Project Structure
```
smart_city_mst/
├── main.py                          ← Entry point (run this)
├── src/
│   ├── datastructures/
│   │   ├── Graph.py                 ← Adjacency list graph
│   │   ├── UnionFind.py             ← DSU for Kruskal's
│   │   └── MinHeap.py               ← Min-heap for Prim's
│   └── algorithms/
│       ├── Prims.py                 ← Prim's  O(E log V)
│       ├── Kruskals.py              ← Kruskal's O(E log E)
│       ├── BruteForce.py            ← Exhaustive O(V^V)
│       └── ComplexityAnalyser.py    ← Benchmarks & theory
├── tests/
│   └── test_all.py                  ← 39 unit tests (all pass)
└── smart_city_mst.html              ← Interactive GUI
```

### How to Run

```bash
# Full demo + benchmark
python main.py

# Demo only
python main.py --demo

# Complexity theory tables
python main.py --theory

# Empirical benchmark
python main.py --bench

# Side-by-side comparison
python main.py --compare

# Enter your own graph interactively
python main.py --custom

# Run all tests
python tests/test_all.py
```

### Algorithms

| Algorithm    | Technique          | Time        | Space    | Data Structure        |
|--------------|--------------------|-------------|----------|-----------------------|
| Prim's       | Greedy (Cut Prop)  | O(E log V)  | O(V+E)   | Min-Heap + Adj. List  |
| Kruskal's    | Greedy (Cycle Prop)| O(E log E)  | O(V+E)   | Union-Find + Sort     |
| Brute Force  | Exhaustive Search  | O(V^V)      | O(V²)    | Combinations + BFS    |

### Why Prim's and Kruskal's get the same cost
Both algorithms are provably correct for finding MSTs. The MST cost is
**unique** (even if the edge set differs on tie weights). Both are guaranteed
to find this minimum by the Cut Property and Cycle Property of MSTs respectively.
