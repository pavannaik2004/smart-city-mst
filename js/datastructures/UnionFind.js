/**
 * datastructures/UnionFind.js
 * ============================================================
 * Disjoint-Set Union (DSU) with path compression + union by
 * rank — the data structure behind Kruskal's cycle check and
 * brute force's spanning-tree validation.
 *
 * Without it, "are a and b already connected?" would need a
 * graph traversal (O(V + E)) every time an edge is considered.
 * With union by rank + path compression, find()/union() are
 * O(log V) worst case and effectively O(1) amortised in
 * practice (technically O(α(V)), the inverse Ackermann
 * function) — which is why Kruskal's E-edge loop adds only
 * O(E) on top of the O(E log E) sort, not O(E·V).
 * ============================================================
 */

export class UnionFind {
  /** @param {number[]} ids initial set of singleton elements */
  constructor(ids = []) {
    this.parent = new Map();
    this.rank = new Map();
    ids.forEach((id) => {
      this.parent.set(id, id);
      this.rank.set(id, 0);
    });
  }

  _ensure(x) {
    if (!this.parent.has(x)) {
      this.parent.set(x, x);
      this.rank.set(x, 0);
    }
  }

  /** Finds the representative (root) of x's set, compressing the path as it goes. */
  find(x) {
    this._ensure(x);
    if (this.parent.get(x) !== x) {
      this.parent.set(x, this.find(this.parent.get(x)));
    }
    return this.parent.get(x);
  }

  /** Merges the sets containing a and b. Returns false if they were already the same set (i.e. union(a,b) would close a cycle). */
  union(a, b) {
    const ra = this.find(a);
    const rb = this.find(b);
    if (ra === rb) return false;

    const rankA = this.rank.get(ra);
    const rankB = this.rank.get(rb);
    if (rankA < rankB) {
      this.parent.set(ra, rb);
    } else if (rankA > rankB) {
      this.parent.set(rb, ra);
    } else {
      this.parent.set(rb, ra);
      this.rank.set(ra, rankA + 1);
    }
    return true;
  }

  connected(a, b) {
    return this.find(a) === this.find(b);
  }
}
