// Mirrors backend/app/metrics.py so the form can preview results before saving.

const has = (v) => v != null && !Number.isNaN(v)

export function tradeMetrics({ side, entry, exit, size, stop, takeProfit, fees }) {
  const dir = side === 'short' ? -1 : 1
  const riskPerUnit = has(entry) && has(stop) && entry !== stop ? Math.abs(entry - stop) : null
  const risk = riskPerUnit && has(size) ? riskPerUnit * size : null
  const grossPnl = has(entry) && has(exit) && has(size) ? (exit - entry) * size * dir : null
  const pnl = grossPnl == null ? null : grossPnl - (has(fees) ? fees : 0)
  return {
    grossPnl,
    pnl, // net of fees
    rMultiple: risk && pnl != null ? pnl / risk : null,
    risk,
    plannedRR: riskPerUnit && has(takeProfit) ? Math.abs(takeProfit - entry) / riskPerUnit : null,
  }
}
