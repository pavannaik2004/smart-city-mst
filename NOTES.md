# Study Notes — Smart City MST Planner

Notes for explaining the code and the underlying DAA (Design & Analysis
of Algorithms) theory: what each file does, how Prim's and Kruskal's
actually work, and how the complexity figures shown in the app are
derived. Written to be read top-to-bottom once, then used as a
reference during a viva/demo.

---

## 1. The big picture

The app lets you draw a weighted graph (sensor nodes + wiring costs)
and watch three algorithms compute its **Minimum Spanning Tree (MST)**
— the cheapest set of edges that connects every node with no cycles.

```
css/styles.css          presentation only

js/main.js              entry point — wires buttons, boots the app
js/app.js               shared state + UI + presets + "run" controller
js/canvas.js            drawing the graph, click/drag editing, pan/zoom

js/algorithms/
  prims.js              Prim's algorithm
  kruskals.js           Kruskal's algorithm
  bruteforce.js         exhaustive search baseline

js/datastructures/
  Graph.js              adjacency list
  MinHeap.js            binary min-heap (priority queue)
  UnionFind.js          disjoint-set union (DSU)

js/complexityAnalyzer.js   theoretical Big-O calculator (static analysis)
js/timeAnalyzer.js         empirical performance.now() timing (dynamic analysis)
```

**Key idea to articulate in a viva:** the algorithms folder is *what*
runs, the datastructures folder is *what it runs on top of*, and the
two analyzer files are *how fast it is, predicted vs. measured*. That
three-way split (algorithm / data structure / complexity) is the
whole point of a DAA project.

---

## 2. Data structures — why each one exists

### 2.1 `Graph.js` — adjacency list
[js/datastructures/Graph.js](js/datastructures/Graph.js)

A `Map<nodeId, [{to, weight, edgeRef}]>`. Each undirected edge is
stored **twice** (once per endpoint), so `edgeCount()` divides by 2.

- **Why adjacency list, not a matrix?** A matrix is O(V²) space and a
  full row-scan to find neighbours. Road/sensor networks are sparse
  (E ≪ V²), so a list costs O(V + E) space and O(deg(v)) to list a
  node's neighbours — this is *why* Prim's and Kruskal's end up
  near-linear in input size instead of quadratic in V.
- `isConnected()` is a plain BFS — O(V + E) — used as the
  precondition check before running any MST algorithm: **an MST only
  exists if the graph is connected.**

### 2.2 `MinHeap.js` — binary min-heap (priority queue)
[js/datastructures/MinHeap.js](js/datastructures/MinHeap.js)

Classic array-backed binary heap. For index `i`: children at `2i+1`,
`2i+2`; parent at `(i-1)>>1`.

- `push`: append to the end, then **bubble up** (swap with parent
  while smaller) — O(log n).
- `pop`: save the root, move the *last* element into the root slot,
  then **bubble down** (swap with smaller child) — O(log n).
- This is the data structure that turns "scan all edges to find the
  minimum" (O(E) per step) into "ask the heap for the minimum"
  (O(log V) per step) — it's where the **log V** in Prim's O((V+E) log V)
  literally comes from.

### 2.3 `UnionFind.js` — disjoint-set union (DSU)
[js/datastructures/UnionFind.js](js/datastructures/UnionFind.js)

Answers **"are these two nodes already connected?"** without walking
the graph, by keeping every node's *set representative* (root).

- `find(x)`: follow `parent` pointers to the root, **path-compressing**
  along the way (every visited node gets repointed straight to the
  root) — flattens the tree for next time.
- `union(a, b)`: find both roots; if equal, they're already connected
  → return `false` (this is the **cycle check**). Otherwise attach the
  smaller-rank tree under the larger one (**union by rank**) → return
  `true`.
- With both optimizations, find/union are O(log V) worst case and
  effectively **O(1) amortised** in practice (technically O(α(V)), the
  inverse Ackermann function — grows so slowly it's a constant for any
  realistic input).
- Used by **Kruskal's** (cycle check) and by **brute force**
  (spanning-tree validation — see §5).

---

## 3. Prim's algorithm
[js/algorithms/prims.js](js/algorithms/prims.js)

### Idea
Grow **one tree**, starting from an arbitrary node. At every step, look
at the **cut** between "nodes already in the tree" and "nodes not yet
in the tree", and add the cheapest edge crossing that cut. Repeat
until every node is in the tree.

### Why it's correct — the Cut Property
> For any cut of the graph (any way of splitting nodes into two
> non-empty groups), the minimum-weight edge crossing that cut belongs
> to *some* MST (assuming unique weights, or with a consistent
> tie-break).

Picking the cheapest crossing edge at every step never makes a choice
you'd have to undo later — that's why a *greedy* algorithm gives the
*globally optimal* answer here, which is the headline result to be
able to explain.

### How the code implements it
1. Build a `Graph` from the current nodes/edges ([prims.js:39](js/algorithms/prims.js#L39)).
2. Mark the start node visited, push its incident edges onto a `MinHeap`
   keyed by weight ([prims.js:46-47](js/algorithms/prims.js#L46-L47)).
3. Loop: pop the cheapest heap entry. If its far endpoint is already
   visited, **discard and pop again** — this is "**lazy deletion**": rather
   than removing stale entries from the middle of the heap (expensive),
   we just skip them when popped ([prims.js:64-66](js/algorithms/prims.js#L64-L66)).
4. Otherwise that edge is accepted into the MST; mark the new node
   visited and push *its* incident edges too ([prims.js:68-74](js/algorithms/prims.js#L68-L74)).
5. Stop when every node is visited.

The edge-scan loop you also see in the code (`for (const e of edges) ...
e.animating = true`) is **purely cosmetic** — it highlights the
frontier for the animation. The heap, not that scan, is what actually
picks the next edge.

### Complexity
- Every edge is pushed at most twice (once from each endpoint) and
  popped at most once → O(E) heap operations, each O(log V) →
  **Time: O((V + E) log V)**.
- **Space: O(V + E)** — the adjacency list plus the heap.
- Best for **dense** graphs (large E relative to V), because it never
  has to sort the whole edge list up front.

---

## 4. Kruskal's algorithm
[js/algorithms/kruskals.js](js/algorithms/kruskals.js)

### Idea
Sort **all** edges by weight. Walk them cheapest-first. Accept an edge
unless it connects two nodes that are *already* in the same component
(accepting it would create a cycle). Stop once you've accepted `V-1`
edges.

### Why it's correct — the Cycle Property
> For any cycle in the graph, the single most expensive edge on that
> cycle is **never** needed in an MST — there's always a cheaper way
> around.

Rejecting an edge that would close a cycle is therefore always safe:
you're never throwing away an edge an optimal MST actually needed.

### How the code implements it
1. Build a `UnionFind` over all node ids ([kruskals.js:36](js/algorithms/kruskals.js#L36)).
2. `sorted = [...edges].sort((a,b) => a.weight - b.weight)` — sort once
   ([kruskals.js:38](js/algorithms/kruskals.js#L38)).
3. For each edge in sorted order: `uf.union(e.from, e.to)`.
   - Returns `true` → they were in different components → **accept**,
     add to `mstEdges` ([kruskals.js:55-56](js/algorithms/kruskals.js#L55-L56)).
   - Returns `false` → both endpoints already connected → **reject**
     (would form a cycle) ([kruskals.js:64-65](js/algorithms/kruskals.js#L64-L65)).
4. Stop early once `mstEdges.length === nodes.length - 1` — the tree
   is complete, no need to look at the rest of the sorted list
   ([kruskals.js:63](js/algorithms/kruskals.js#L63)).

### Complexity
- Sorting E edges: O(E log E) — this **dominates** the runtime.
- Then E calls to `union`/`find`, each ~O(1) amortised (DSU with path
  compression + union by rank) → +O(E), which doesn't change the
  overall class.
- **Time: O(E log E)**. **Space: O(V + E)**.
- Best for **sparse** graphs (small E relative to V), because the cost
  is driven by E, not by how many nodes there are.

### Prim's vs. Kruskal's — the question every viva asks
| | Prim's | Kruskal's |
|---|---|---|
| Grows | one tree, outward from a start node | many fragments, merging as edges are accepted |
| Driven by | the **cut** (frontier of the current tree) | the **cycle** (would this edge close one?) |
| Data structure | MinHeap | Sort + UnionFind |
| Time | O((V+E) log V) | O(E log E) |
| Better for | dense graphs | sparse graphs |
| Always agree on... | **total MST cost** (provably unique) — even if the *specific edges* chosen differ on tied weights |

You can demonstrate this last row directly in the app: run Prim's then
Kruskal's on the same graph and compare `MST COST` in the Results panel
— they always match.

---

## 5. Brute force (the baseline)
[js/algorithms/bruteforce.js](js/algorithms/bruteforce.js)

### Idea
Don't be clever — try every possible spanning tree and keep the
cheapest. This exists purely so the greedy algorithms above have
something to be compared *against* (correctness and speed).

### How the code implements it
1. `generateSubsets(edges, V-1)` enumerates **every combination** of
   `V-1` edges out of `E` — i.e. every candidate edge-set a spanning
   tree could be made from ([bruteforce.js:40-55](js/algorithms/bruteforce.js#L40-L55)).
2. For each candidate, `isSpanningTree()` checks it's valid using a
   **fresh UnionFind**: union every edge in the subset; if any union
   call returns `false` it's not a tree (has a cycle); if all nodes end
   up under one root, it's a spanning tree ([bruteforce.js:58-66](js/algorithms/bruteforce.js#L58-L66)).
3. Track the minimum-cost valid subset seen.
4. A hard cap (`MAX_ATTEMPTS = 200`) prevents the browser tab from
   freezing on a large random graph ([bruteforce.js:33](js/algorithms/bruteforce.js#L33)).

### Complexity — implementation vs. textbook bound
This is a subtlety worth calling out explicitly:
- The **textbook** brute-force bound usually quoted is **O(V^V)**
  ("try every labelled tree on V nodes" — Cayley's formula says there
  are exactly V^(V-2) labelled trees, rounded up to V^V as a loose
  bound).
- **This implementation** doesn't enumerate labelled trees in the
  abstract — it enumerates `(V-1)`-edge combinations *from the actual
  edge list*, which is `C(E, V-1)`, each validated in O(V). That's a
  *tighter*, implementation-accurate bound:
  **Time: O(C(E, V-1) · V)**. **Space: O(V²)** (the UnionFind's parent/rank maps).
- `complexityAnalyzer.js` reports both numbers (see §6) — being able
  to explain *why* there are two different complexity figures for the
  same algorithm is a good sign of actually understanding the analysis,
  not just quoting it.

---

## 6. `complexityAnalyzer.js` — theoretical (static) analysis
[js/complexityAnalyzer.js](js/complexityAnalyzer.js)

This is the "calculate time complexity" function set: given the
**current graph's** V (node count) and E (edge count), it plugs them
into each algorithm's formula to get a concrete number — not just a
symbol.

```js
primComplexity(V, E)        → ops = (V + E) * log2(V)
kruskalComplexity(V, E)     → ops = E * log2(E) + E
bruteForceComplexity(V, E)  → combos = C(E, V-1); ops = combos * V
```

- `log2(x)` is used because heap and sort operation counts are
  naturally expressed in base-2 (each comparison halves a search
  space / heap level).
- `binomial(n, k)` computes `C(n, k)` **iteratively** (multiply-then-divide
  one term at a time) instead of `n! / (k! (n-k)!)`, to avoid factorial
  overflow for even modest n.
- `renderComplexityPanel(V, E)` is the function that turns these
  numbers into the live "Complexity Analysis" panel in the UI —
  re-run every time the graph changes (`app.js#updateCounts` calls it),
  so the Big-O **labels never go stale** relative to what's on the
  canvas.

**Why this matters for "analysis of algorithms":** stating "O(E log E)"
is the *qualitative* class; plugging in real V/E to get "~61 estimated
operations" is what makes it an *analysis* — you can watch the number
grow as you add sensors and see the growth rate match the Big-O class.

---

## 7. `timeAnalyzer.js` — empirical (dynamic) analysis
[js/timeAnalyzer.js](js/timeAnalyzer.js)

The counterpart to §6: instead of predicting, it **measures**.

```js
export async function runTimedAlgorithm(algoFn) {
  const t0 = performance.now();
  await algoFn();
  return { elapsedMs: performance.now() - t0 };
}
```

- `performance.now()` is used instead of `Date.now()` because it's
  **monotonic and sub-millisecond**: it can't go backwards if the
  system clock is adjusted, and it's precise enough to time something
  that finishes in a few milliseconds.
- `compareToPrevious(history, algoKey, V, E, elapsedMs)` remembers the
  last run of each algorithm and reports how the input size and the
  measured time *both* changed (`sizeRatio`, `timeRatio`) — e.g. "input
  ×2.1, time ×4.3" is a quick empirical hint that an algorithm is
  scaling worse than linearly.

`app.js#runAlgo` ([js/app.js](js/app.js)) is what stitches §6 and §7
together for each run:
1. Before running: log the **theoretical estimate** from
   `complexityAnalyzer.js`.
2. Run the algorithm, timed via `timeAnalyzer.js`.
3. After running: log the **measured time**, right next to the
   estimate, plus the growth-vs-last-run comparison.

That before/after pairing in the log panel *is* the theoretical vs.
empirical complexity comparison — the whole reason this project has
two separate analyzer files instead of one.

---

## 8. Quick reference table

| Algorithm | Greedy rule | Data structure | Time | Space |
|---|---|---|---|---|
| Prim's | cheapest edge across the cut | MinHeap + Graph | O((V+E) log V) | O(V+E) |
| Kruskal's | cheapest edge that avoids a cycle | sort + UnionFind | O(E log E) | O(V+E) |
| Brute force | none — exhaustive | UnionFind (validation) | O(C(E,V-1)·V); textbook bound O(V^V) | O(V²) |

## 9. Likely viva questions (with where to point)

- *"Why does Prim's use a heap?"* → §2.2 / §3 — turns an O(E) linear
  scan into an O(log V) heap operation per step.
- *"What's lazy deletion and why not just remove the stale entry?"* →
  [prims.js:64-66](js/algorithms/prims.js#L64-L66) — removing from the middle of a heap isn't a
  native O(log n) operation; it's simpler and just as fast to leave
  stale entries and skip them on pop.
- *"Why does Kruskal's need Union-Find instead of just checking with
  BFS?"* → §2.3 — BFS-per-edge would be O(V+E) each, O(E(V+E)) total;
  Union-Find makes the same check ~O(1) amortised.
- *"Why do Prim's and Kruskal's always produce the same cost but maybe
  different edges?"* → §3's Cut Property + §4's Cycle Property — two
  different proofs of optimality, same minimum, not necessarily the
  same edge set on ties.
- *"Why is brute force's complexity shown as two different formulas?"*
  → §5 — implementation-accurate `O(C(E,V-1)·V)` vs. the textbook
  worst-case bound `O(V^V)`.
- *"What's the difference between the two analyzer files?"* → §6 vs §7
  — one predicts from a formula (static), one measures a real run with
  `performance.now()` (dynamic/empirical).
