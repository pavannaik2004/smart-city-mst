# Smart City Road Network Planner
## Minimum Spanning Tree — Interactive Visualizer & Complexity Analyzer

A browser-based tool for designing a sensor/road network and watching
**Prim's**, **Kruskal's**, and a **brute-force** exhaustive search find
its Minimum Spanning Tree step by step — built as a teaching aid for an
Analysis & Design of Algorithms (DAA) project: it doesn't just show the
answer, it shows the algorithm *and* a calculator for its complexity.

🔗 Live demo: deployed automatically to GitHub Pages from `main`
(see [.github/workflows/pages.yml](.github/workflows/pages.yml)).

### Project Structure

```
smart_city_mst/
├── index.html                       ← redirects to smart_city_mst.html
├── smart_city_mst.html              ← page markup only (no inline logic)
├── css/
│   └── styles.css                   ← all presentation/styling
└── js/
    ├── main.js                      ← entry point: wires up buttons, boots the app
    ├── app.js                       ← shared state, DOM refs, UI/presets/run controller
    ├── canvas.js                    ← canvas rendering, hit-testing, pan/zoom, editing
    ├── complexityAnalyzer.js        ← theoretical Big-O calculator (live, per V/E)
    ├── timeAnalyzer.js              ← empirical run-time measurement & comparison
    ├── algorithms/
    │   ├── prims.js                 ← Prim's   O((V + E) log V)
    │   ├── kruskals.js              ← Kruskal's O(E log E)
    │   └── bruteforce.js            ← Exhaustive search O(C(E, V-1) · V)
    └── datastructures/
        ├── Graph.js                 ← adjacency-list graph
        ├── MinHeap.js                ← binary min-heap (powers Prim's)
        └── UnionFind.js              ← disjoint-set / DSU (powers Kruskal's + brute force)
```

Every file has a doc comment at the top explaining *what it does and
why it's built that way* — start with `js/algorithms/` and
`js/datastructures/` if you're here for the algorithms course content.

### How to Run

The JS is loaded as ES modules (`<script type="module">`), which
browsers refuse to load over the `file://` protocol. Serve the folder
over HTTP instead of double-clicking the HTML file:

```bash
# from the project root, pick one:
python -m http.server 8000
# or: npx serve .

# then open:
http://localhost:8000/smart_city_mst.html
```

On GitHub Pages this just works as-is — no server step needed there.

### What you can do in the UI

- **Build a graph by hand** — add sensor nodes, connect them with
  weighted edges, or delete either.
- **Load a preset** — an 8-node city grid, a hub-and-spoke topology,
  or a random graph (2–12 nodes).
- **Run an algorithm** — animated step-by-step, with a running log
  explaining each decision (why an edge was accepted/rejected, etc).
- **Read live complexity numbers** — the "Complexity Analysis" panel
  recalculates each algorithm's Big-O class *and* an estimated
  operation count every time the graph changes, and the run log
  prints that estimate against the actually-measured run time.

### Algorithms

| Algorithm    | Technique           | Time                 | Space  | Data Structure        |
|--------------|----------------------|-----------------------|--------|------------------------|
| Prim's       | Greedy (Cut Property)  | O((V + E) log V)     | O(V+E) | MinHeap + Graph        |
| Kruskal's    | Greedy (Cycle Property)| O(E log E)           | O(V+E) | UnionFind + sort       |
| Brute Force  | Exhaustive search       | O(C(E, V-1) · V)     | O(V²)  | UnionFind (validation) |

Brute force's complexity above is the *actual* cost of how it's
implemented (try every `(V-1)`-edge combination, validate with
Union-Find) — tighter than, and shown alongside, the textbook
"try every labelled tree" bound of `O(V^V)`.

### Why Prim's and Kruskal's always agree

Both are provably correct MST algorithms. The MST's total cost is
**unique** even when the edge set isn't (ties can be broken
differently). Prim's correctness comes from the **Cut Property**;
Kruskal's from the **Cycle Property** — different proofs, same
guaranteed-minimum result, which the app lets you confirm by running
both on the same graph and comparing `MST COST`.
