/**
 * datastructures/Graph.js
 * ============================================================
 * Adjacency-list graph — the representation every MST algorithm
 * in this project is built on top of.
 *
 * Why adjacency list (and not an adjacency matrix)?
 *   - Listing the neighbours of a node costs O(deg(node)), and
 *     summed over all nodes that's O(V + E) total, vs O(V²) for
 *     a matrix. Since road networks / sensor grids are sparse
 *     (E is much smaller than V²), this is the right trade-off
 *     and is exactly what makes Prim's O((V+E) log V) and
 *     Kruskal's O(E log E) — both are linear-ish in the input
 *     size, not quadratic in V.
 *   - Space: O(V + E) — one map entry per node, two adjacency
 *     records per edge (undirected).
 * ============================================================
 */

export class Graph {
  constructor() {
    /** @type {Map<number, {to:number, weight:number, edgeRef:object}[]>} */
    this.adj = new Map();
  }

  addNode(id) {
    if (!this.adj.has(id)) this.adj.set(id, []);
  }

  /** Adds an undirected edge. `edgeRef` is kept so callers can map back to the original edge object (for highlighting/animation). */
  addEdge(a, b, weight, edgeRef) {
    this.addNode(a);
    this.addNode(b);
    this.adj.get(a).push({ to: b, weight, edgeRef });
    this.adj.get(b).push({ to: a, weight, edgeRef });
  }

  /** @returns {{to:number, weight:number, edgeRef:object}[]} the edges leaving `id`. */
  neighbors(id) {
    return this.adj.get(id) || [];
  }

  nodeIds() {
    return [...this.adj.keys()];
  }

  nodeCount() {
    return this.adj.size;
  }

  /** Each undirected edge is stored twice (once per endpoint), hence the /2. */
  edgeCount() {
    let total = 0;
    for (const list of this.adj.values()) total += list.length;
    return total / 2;
  }

  /**
   * BFS reachability from an arbitrary start node — O(V + E).
   * An MST only exists if the graph is connected.
   */
  isConnected() {
    const ids = this.nodeIds();
    if (ids.length === 0) return false;
    const visited = new Set([ids[0]]);
    const queue = [ids[0]];
    while (queue.length) {
      const cur = queue.shift();
      for (const { to } of this.neighbors(cur)) {
        if (!visited.has(to)) {
          visited.add(to);
          queue.push(to);
        }
      }
    }
    return visited.size === ids.length;
  }

  /** Builds a Graph from the app's flat {nodes, edges} arrays (see state in app.js). */
  static fromNodesEdges(nodes, edges) {
    const g = new Graph();
    nodes.forEach((n) => g.addNode(n.id));
    edges.forEach((e) => g.addEdge(e.from, e.to, e.weight, e));
    return g;
  }
}
