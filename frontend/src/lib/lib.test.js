import { describe, expect, it } from 'vitest'
import { buildMonthGrid } from './calendar.js'
import { tradeMetrics } from './tradeMath.js'

describe('tradeMetrics', () => {
  it('matches the backend for a long winner', () => {
    const m = tradeMetrics({ side: 'long', entry: 100, exit: 110, size: 10, stop: 95, takeProfit: 115 })
    expect(m).toEqual({ pnl: 100, rMultiple: 2, risk: 50, plannedRR: 3 })
  })

  it('flips direction for shorts', () => {
    const m = tradeMetrics({ side: 'short', entry: 100, exit: 105, size: 2, stop: 105, takeProfit: null })
    expect(m.pnl).toBe(-10)
    expect(m.rMultiple).toBe(-1)
  })

  it('returns nulls for an open trade without a stop', () => {
    const m = tradeMetrics({ side: 'long', entry: 100, exit: null, size: 1, stop: null, takeProfit: null })
    expect(m).toEqual({ pnl: null, rMultiple: null, risk: null, plannedRR: null })
  })
})

describe('buildMonthGrid', () => {
  it('starts weeks on Monday and pads to full weeks', () => {
    // October 2026 starts on a Thursday and has 31 days.
    const weeks = buildMonthGrid(2026, 9)
    expect(weeks[0]).toEqual([null, null, null, '2026-10-01', '2026-10-02', '2026-10-03', '2026-10-04'])
    expect(weeks.every((w) => w.length === 7)).toBe(true)
    expect(weeks.flat().filter(Boolean)).toHaveLength(31)
  })
})
