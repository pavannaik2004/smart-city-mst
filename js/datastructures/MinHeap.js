/**
 * datastructures/MinHeap.js
 * ============================================================
 * Binary min-heap (array-backed priority queue) — the data
 * structure that gives Prim's algorithm its O(log V) per
 * insert/extract-min, which is where the "log V" in
 * O((V + E) log V) actually comes from.
 *
 * Standard array layout: for index i, children live at
 * 2i+1 and 2i+2, parent at floor((i-1)/2). push() is
 * "insert then bubble up", pop() is "remove root, pull the
 * last leaf into its place, then bubble down".
 *
 *   push / pop: O(log n)
 *   peek:       O(1)
 *   space:      O(n)
 * ============================================================
 */

export class MinHeap {
  /** @param {(a:any,b:any) => number} compare returns <0 if a has higher priority than b */
  constructor(compare = (a, b) => a - b) {
    this.items = [];
    this.compare = compare;
  }

  get size() {
    return this.items.length;
  }

  isEmpty() {
    return this.items.length === 0;
  }

  peek() {
    return this.items[0];
  }

  push(item) {
    this.items.push(item);
    this._bubbleUp(this.items.length - 1);
  }

  /** Removes and returns the minimum element, or undefined if empty. */
  pop() {
    if (this.items.length === 0) return undefined;
    const top = this.items[0];
    const last = this.items.pop();
    if (this.items.length > 0) {
      this.items[0] = last;
      this._bubbleDown(0);
    }
    return top;
  }

  _bubbleUp(i) {
    while (i > 0) {
      const parent = (i - 1) >> 1;
      if (this.compare(this.items[i], this.items[parent]) >= 0) break;
      this._swap(i, parent);
      i = parent;
    }
  }

  _bubbleDown(i) {
    const n = this.items.length;
    while (true) {
      const left = 2 * i + 1;
      const right = 2 * i + 2;
      let smallest = i;
      if (left < n && this.compare(this.items[left], this.items[smallest]) < 0) smallest = left;
      if (right < n && this.compare(this.items[right], this.items[smallest]) < 0) smallest = right;
      if (smallest === i) break;
      this._swap(i, smallest);
      i = smallest;
    }
  }

  _swap(i, j) {
    [this.items[i], this.items[j]] = [this.items[j], this.items[i]];
  }
}
