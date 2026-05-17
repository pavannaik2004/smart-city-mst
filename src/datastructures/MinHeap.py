"""
╔══════════════════════════════════════════════════════════════════╗
║  MinHeap.py — Binary Min-Heap (Priority Queue)                   ║
╠══════════════════════════════════════════════════════════════════╣
║  Used by Prim's algorithm to always extract the cheapest edge.   ║
║  insert       : O(log n)                                         ║
║  extract_min  : O(log n)                                         ║
║  decrease_key : O(log n)  — via position map                     ║
║  peek         : O(1)                                             ║
║  SPACE        : O(n)                                             ║
╚══════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from typing import Any, Optional


class HeapNode:
    """
    A node inside the min-heap.

    Attributes
    ----------
    key     : priority value (edge weight)
    vertex  : graph node ID this entry belongs to
    data    : optional payload (e.g. parent vertex)
    """

    def __init__(self, key: float, vertex: int, data: Any = None):
        self.key    = key
        self.vertex = vertex
        self.data   = data

    def __lt__(self, other: HeapNode) -> bool:
        return self.key < other.key

    def __repr__(self) -> str:
        return f"HeapNode(key={self.key}, S{self.vertex})"


class MinHeap:
    """
    Binary Min-Heap with O(log n) decrease-key via a position map.

    The position map (self._pos) tracks each vertex's index in the
    underlying array so decrease_key can find and bubble-up the entry
    in O(log n) instead of O(n).

    Without this optimisation, Prim's would degrade to O(V²).
    With it, Prim's runs in O(E log V).

    Example
    -------
        heap = MinHeap()
        heap.insert(HeapNode(0,   1))   # start vertex, cost 0
        heap.insert(HeapNode(inf, 2))   # unvisited, cost ∞
        heap.insert(HeapNode(inf, 3))

        node = heap.extract_min()       # → HeapNode(key=0, S1)
        heap.decrease_key(2, 5)         # discovered edge cost=5 to S2
    """

    def __init__(self):
        self._heap: list[HeapNode]   = []
        self._pos:  dict[int, int]   = {}   # vertex → index in heap array

    # ── Public Interface ──────────────────────────────────────────────

    def insert(self, node: HeapNode) -> None:
        """Insert and bubble-up. Time: O(log n)."""
        self._heap.append(node)
        idx = len(self._heap) - 1
        self._pos[node.vertex] = idx
        self._bubble_up(idx)

    def extract_min(self) -> HeapNode:
        """Remove and return the minimum-key node. Time: O(log n)."""
        if self.is_empty():
            raise IndexError("Heap is empty")
        self._swap(0, len(self._heap) - 1)
        minimum = self._heap.pop()
        del self._pos[minimum.vertex]
        if self._heap:
            self._bubble_down(0)
        return minimum

    def decrease_key(self, vertex: int, new_key: float) -> bool:
        """
        Decrease the priority key of an existing vertex.
        Used when Prim's finds a cheaper edge to an unvisited node.
        Time: O(log n).

        Returns True if key was decreased, False if not found or not smaller.
        """
        if vertex not in self._pos:
            return False
        idx = self._pos[vertex]
        if new_key >= self._heap[idx].key:
            return False
        self._heap[idx].key = new_key
        self._bubble_up(idx)
        return True

    def update_data(self, vertex: int, data: Any) -> None:
        """Update the data payload of an existing vertex's heap entry."""
        if vertex in self._pos:
            self._heap[self._pos[vertex]].data = data

    def contains(self, vertex: int) -> bool:
        return vertex in self._pos

    def get_key(self, vertex: int) -> Optional[float]:
        if vertex not in self._pos:
            return None
        return self._heap[self._pos[vertex]].key

    def peek(self) -> Optional[HeapNode]:
        return self._heap[0] if self._heap else None

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def size(self) -> int:
        return len(self._heap)

    # ── Internal Helpers ──────────────────────────────────────────────

    def _bubble_up(self, idx: int) -> None:
        """Move node at idx upward until heap property is restored."""
        while idx > 0:
            parent = (idx - 1) // 2
            if self._heap[idx] < self._heap[parent]:
                self._swap(idx, parent)
                idx = parent
            else:
                break

    def _bubble_down(self, idx: int) -> None:
        """Move node at idx downward until heap property is restored."""
        n = len(self._heap)
        while True:
            smallest = idx
            left  = 2 * idx + 1
            right = 2 * idx + 2
            if left  < n and self._heap[left]  < self._heap[smallest]:
                smallest = left
            if right < n and self._heap[right] < self._heap[smallest]:
                smallest = right
            if smallest == idx:
                break
            self._swap(idx, smallest)
            idx = smallest

    def _swap(self, i: int, j: int) -> None:
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]
        self._pos[self._heap[i].vertex] = i
        self._pos[self._heap[j].vertex] = j

    # ── Display ───────────────────────────────────────────────────────

    def display(self) -> None:
        print(f"\n  MinHeap ({len(self._heap)} nodes):")
        for idx, node in enumerate(self._heap):
            parent_idx = (idx - 1) // 2
            bar = "ROOT" if idx == 0 else f"parent=[{parent_idx}]"
            print(f"    [{idx:>2}] S{node.vertex:>2}  key={node.key:<8}  {bar}")
        print()
