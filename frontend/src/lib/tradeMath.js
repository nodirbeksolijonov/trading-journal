// Mirrors backend/app/metrics.py so the form can preview results before saving.

const has = (v) => v != null && !Number.isNaN(v)

export function tradeMetrics({ side, entry, exit, size, stop, takeProfit }) {
  const dir = side === 'short' ? -1 : 1
  const riskPerUnit = has(entry) && has(stop) && entry !== stop ? Math.abs(entry - stop) : null
  return {
    pnl: has(entry) && has(exit) && has(size) ? (exit - entry) * size * dir : null,
    rMultiple: riskPerUnit && has(exit) ? ((exit - entry) * dir) / riskPerUnit : null,
    risk: riskPerUnit && has(size) ? riskPerUnit * size : null,
    plannedRR: riskPerUnit && has(takeProfit) ? Math.abs(takeProfit - entry) / riskPerUnit : null,
  }
}
