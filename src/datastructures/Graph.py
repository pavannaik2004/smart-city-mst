"""
╔══════════════════════════════════════════════════════════════════╗
║           SMART CITY ROAD NETWORK PLANNER                        ║
║           Graph.py — Core Graph Data Structure                   ║
╠══════════════════════════════════════════════════════════════════╣
║  DATA STRUCTURE : Adjacency List  (dict of lists)                ║
║  SPACE          : O(V + E)                                       ║
║  WHY ADJ LIST?  : Sparse graphs → saves memory vs O(V²) matrix   ║
╚══════════════════════════════════════════════════════════════════╝
"""

from collections import defaultdict, deque
from typing import Optional


class Edge:
    """
    Weighted undirected edge between two sensor nodes.

    Attributes
    ----------
    src    : source node ID
    dest   : destination node ID
    weight : connection cost (wiring length / installation cost)
    """

    def __init__(self, src: int, dest: int, weight: int):
        self.src    = src
        self.dest   = dest
        self.weight = weight

    def __lt__(self, other: "Edge") -> bool:
        # Enables sorted() on edges — used by Kruskal's sort step
        return self.weight < other.weight

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Edge):
            return False
        return {self.src, self.dest} == {other.src, other.dest} and self.weight == other.weight

    def __hash__(self) -> int:
        return hash((frozenset([self.src, self.dest]), self.weight))

    def __repr__(self) -> str:
        return f"Edge(S{self.src}─S{self.dest}, cost={self.weight})"


class Graph:
    """
    Weighted Undirected Graph — Adjacency List representation.

    Each node = smart city sensor.
    Each edge = potential wiring connection with a cost.

    Operations
    ----------
    add_node    : O(1)
    add_edge    : O(E)  (duplicate check)
    remove_edge : O(E)
    is_connected: O(V + E)  via BFS

    Example
    -------
        g = Graph()
        g.add_edge(1, 2, 15)
        g.add_edge(2, 3, 20)
        g.display()
    """

    def __init__(self, vertices: int = 0):
        self.vertices: int = vertices
        self.adj: dict[int, list[tuple[int, int]]] = defaultdict(list)
        self.edges: list[Edge] = []
        self._nodes: set[int] = set(range(1, vertices + 1))

    # ── Construction ──────────────────────────────────────────────────

    def add_node(self, node: int) -> None:
        if node not in self._nodes:
            self._nodes.add(node)
            self.vertices += 1

    def add_edge(self, src: int, dest: int, weight: int) -> bool:
        """Add undirected edge. Returns False if already exists."""
        for e in self.edges:
            if {e.src, e.dest} == {src, dest}:
                return False
        self.add_node(src)
        self.add_node(dest)
        edge = Edge(src, dest, weight)
        self.edges.append(edge)
        self.adj[src].append((dest, weight))
        self.adj[dest].append((src, weight))
        return True

    def remove_edge(self, src: int, dest: int) -> bool:
        before = len(self.edges)
        self.edges = [e for e in self.edges if {e.src, e.dest} != {src, dest}]
        self.adj[src]  = [(d, w) for d, w in self.adj[src]  if d != dest]
        self.adj[dest] = [(d, w) for d, w in self.adj[dest] if d != src]
        return len(self.edges) < before

    def remove_node(self, node: int) -> bool:
        if node not in self._nodes:
            return False
        self._nodes.discard(node)
        self.vertices -= 1
        for d, _ in self.adj.get(node, []):
            self.adj[d] = [(x, w) for x, w in self.adj[d] if x != node]
        self.edges = [e for e in self.edges if e.src != node and e.dest != node]
        self.adj.pop(node, None)
        return True

    # ── Queries ───────────────────────────────────────────────────────

    def is_connected(self) -> bool:
        """BFS connectivity check — O(V+E). MST requires connected graph."""
        if not self._nodes:
            return True
        start = next(iter(self._nodes))
        visited = {start}
        queue = deque([start])
        while queue:
            cur = queue.popleft()
            for nbr, _ in self.adj[cur]:
                if nbr not in visited:
                    visited.add(nbr)
                    queue.append(nbr)
        return visited == self._nodes

    def get_edge_weight(self, src: int, dest: int) -> Optional[int]:
        for d, w in self.adj[src]:
            if d == dest:
                return w
        return None

    def get_nodes(self) -> list[int]:
        return sorted(self._nodes)

    def get_edges(self) -> list[Edge]:
        return list(self.edges)

    def node_count(self) -> int:
        return len(self._nodes)

    def edge_count(self) -> int:
        return len(self.edges)

    def degree(self, node: int) -> int:
        return len(self.adj.get(node, []))

    def total_weight(self) -> int:
        return sum(e.weight for e in self.edges)

    # ── Display ───────────────────────────────────────────────────────

    def display(self) -> None:
        sep = "═" * 56
        print(f"\n{sep}")
        print(f"  SENSOR NETWORK GRAPH")
        print(f"  Sensors (nodes) : {self.node_count()}")
        print(f"  Connections     : {self.edge_count()}")
        print(f"  Total wire cost : {self.total_weight()}")
        print(f"  Connected       : {'Yes ✓' if self.is_connected() else 'No ✗'}")
        print(f"{sep}")
        for node in self.get_nodes():
            nbrs = ", ".join(f"S{d}(w={w})" for d, w in sorted(self.adj[node]))
            print(f"  S{node:>2}  →  {nbrs or '(isolated)'}")
        print(f"{sep}\n")

    def display_edge_list(self) -> None:
        print("\n  EDGE LIST (sorted by cost)")
        print("  " + "─" * 34)
        print(f"  {'#':>3}  {'From':>5}  {'To':>5}  {'Cost':>6}")
        print("  " + "─" * 34)
        for i, e in enumerate(sorted(self.edges), 1):
            print(f"  {i:>3}   S{e.src:>2}    S{e.dest:>2}    {e.weight:>5}")
        print("  " + "─" * 34)
