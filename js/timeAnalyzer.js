/**
 * timeAnalyzer.js
 * ============================================================
 * Empirical timing — the "time calculator" half of the toolkit.
 * complexityAnalyzer.js predicts a Big-O class and an estimated
 * operation count *before* a run; this module clocks what the
 * browser actually measured *during* the run, using the
 * high-resolution performance.now() timer (sub-millisecond,
 * monotonic — unaffected by system clock changes, unlike Date.now()).
 *
 * Comparing the two numbers is the empirical-analysis step of
 * the course: does the measured growth track the predicted
 * complexity class as the graph gets bigger?
 * ============================================================
 */

/**
 * Runs an async algorithm function and times it.
 * @param {() => Promise<void>} algoFn
 * @returns {Promise<{elapsedMs: number}>}
 */
export async function runTimedAlgorithm(algoFn) {
  const t0 = performance.now();
  await algoFn();
  const elapsedMs = performance.now() - t0;
  return { elapsedMs };
}

/**
 * Compares a freshly measured run against a previous one for the same
 * algorithm, e.g. after resizing the graph — useful for eyeballing
 * whether runtime is growing roughly linearly, log-linearly, etc.
 * Returns null if there's nothing to compare against yet.
 */
export function compareToPrevious(history, algoKey, V, E, elapsedMs) {
  const prev = history[algoKey];
  history[algoKey] = { V, E, elapsedMs };
  if (!prev) return null;
  const sizeRatio = (V + E) / Math.max(1, prev.V + prev.E);
  const timeRatio = elapsedMs / Math.max(0.001, prev.elapsedMs);
  return { sizeRatio, timeRatio, prev };
}
