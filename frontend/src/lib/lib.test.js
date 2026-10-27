import { describe, expect, it } from 'vitest'
import { buildMonthGrid } from './calendar.js'
import { fmtMoney, fmtR, fmtShortDate, fmtSignedMoney, pnlClass } from './format.js'
import { tradeMetrics } from './tradeMath.js'

describe('format', () => {
  it('never shows a negative zero', () => {
    for (const v of [-0, -0.001, -1e-16]) {
      expect(fmtMoney(v)).toBe('$0.00')
      expect(fmtSignedMoney(v)).toBe('$0.00')
      expect(fmtR(v)).toBe('0.00R')
      expect(pnlClass(v)).toBe('')
    }
  })

  it('keeps real signs', () => {
    expect(fmtSignedMoney(-0.01)).toBe('-$0.01')
    expect(fmtSignedMoney(12.5)).toBe('+$12.50')
    expect(fmtR(-1)).toBe('-1.00R')
  })

  it('formats short dates without timezone shifts', () => {
    expect(fmtShortDate('2026-10-01')).toBe('Oct 1')
    expect(fmtShortDate('2026-01-31', true)).toBe('Jan 31, 2026')
  })
})

describe('tradeMetrics', () => {
  it('matches the backend for a long winner', () => {
    const m = tradeMetrics({ side: 'long', entry: 100, exit: 110, size: 10, stop: 95, takeProfit: 115 })
    expect(m).toEqual({ grossPnl: 100, pnl: 100, rMultiple: 2, risk: 50, plannedRR: 3 })
  })

  it('takes fees out of P&L and R', () => {
    const m = tradeMetrics({ side: 'long', entry: 100, exit: 110, size: 10, stop: 95, takeProfit: null, fees: 10 })
    expect(m.grossPnl).toBe(100)
    expect(m.pnl).toBe(90)
    expect(m.rMultiple).toBeCloseTo(1.8)
  })

  it('flips direction for shorts', () => {
    const m = tradeMetrics({ side: 'short', entry: 100, exit: 105, size: 2, stop: 105, takeProfit: null })
    expect(m.pnl).toBe(-10)
    expect(m.rMultiple).toBe(-1)
  })

  it('returns nulls for an open trade without a stop', () => {
    const m = tradeMetrics({ side: 'long', entry: 100, exit: null, size: 1, stop: null, takeProfit: null })
    expect(m).toEqual({ grossPnl: null, pnl: null, rMultiple: null, risk: null, plannedRR: null })
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
