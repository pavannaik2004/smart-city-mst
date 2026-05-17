"""
╔══════════════════════════════════════════════════════════════════╗
║  UnionFind.py — Disjoint Set Union (DSU)                         ║
╠══════════════════════════════════════════════════════════════════╣
║  Used by Kruskal's to detect cycles in near-constant time.       ║
║  Optimisations: Path Compression + Union by Rank                 ║
║  TIME  per operation: O(α(V)) ≈ O(1)  (inverse Ackermann)        ║
║  SPACE: O(V)                                                     ║
╚══════════════════════════════════════════════════════════════════╝
"""


class UnionFind:
    """
    Disjoint Set Union with Path Compression and Union by Rank.

    Why this beats a naive cycle check (DFS each time):
      - Naive: O(V) per edge  →  O(E·V) total
      - DSU  : O(α(V)) per edge  →  essentially O(E) total

    Parameters
    ----------
    nodes : list of node IDs to initialise

    Example
    -------
        uf = UnionFind([1, 2, 3, 4, 5])
        uf.union(1, 2)   # True  — merged
        uf.union(2, 1)   # False — already same component (cycle!)
        uf.find(1) == uf.find(2)   # True
    """

    def __init__(self, nodes: list[int]):
        # Each node starts as its own parent (singleton component)
        self.parent: dict[int, int] = {n: n for n in nodes}
        self.rank:   dict[int, int] = {n: 0 for n in nodes}
        self._components: int = len(nodes)
        self._union_history: list[tuple[int, int, bool]] = []

    # ── Core Operations ───────────────────────────────────────────────

    def find(self, x: int) -> int:
        """
        Find root of x's component.
        PATH COMPRESSION: flattens the tree on the way up → O(α(V)).
        """
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])   # compress path
        return self.parent[x]

    def union(self, a: int, b: int) -> bool:
        """
        Merge sets containing a and b.

        UNION BY RANK: attach shorter tree under taller tree to keep
        the tree shallow — prevents O(V) degenerate chains.

        Returns
        -------
        True  — merge succeeded (different components)
        False — already in same component → adding this edge = CYCLE
        """
        root_a, root_b = self.find(a), self.find(b)
        self._union_history.append((a, b, root_a != root_b))

        if root_a == root_b:
            return False   # cycle detected!

        # Attach lower-rank tree under higher-rank root
        if self.rank[root_a] < self.rank[root_b]:
            root_a, root_b = root_b, root_a

        self.parent[root_b] = root_a
        if self.rank[root_a] == self.rank[root_b]:
            self.rank[root_a] += 1
        self._components -= 1
        return True

    def connected(self, a: int, b: int) -> bool:
        return self.find(a) == self.find(b)

    def component_count(self) -> int:
        return self._components

    # ── Display ───────────────────────────────────────────────────────

    def display(self) -> None:
        print("\n  ┌─ Union-Find Internal State ─────────────────────┐")
        print(f"  │  {'Node':>5}  │  {'Parent':>6}  │  {'Root':>6}  │  {'Rank':>5}  │")
        print(f"  │  {'─'*5}  │  {'─'*6}  │  {'─'*6}  │  {'─'*5}  │")
        for n in sorted(self.parent):
            print(f"  │  S{n:>3}   │  S{self.parent[n]:>4}   │  S{self.find(n):>4}   │  {self.rank[n]:>5}  │")
        print(f"  │  Components: {self._components:<35}│")
        print("  └──────────────────────────────────────────────────┘\n")

    def display_history(self) -> None:
        print("\n  Union Operations History:")
        for i, (a, b, merged) in enumerate(self._union_history, 1):
            status = "MERGED ✓" if merged else "CYCLE  ✗ (rejected)"
            print(f"    {i:>3}. union(S{a}, S{b}) → {status}")
