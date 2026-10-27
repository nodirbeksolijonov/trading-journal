import { describe, expect, it } from 'vitest'
import { dayBounds, formatTick, timeTicks, toTimeSeries } from './timeScale.js'

const local = (y, m, d, h = 0) => new Date(y, m - 1, d, h).getTime()

describe('toTimeSeries', () => {
  it('places x by date and spreads same-day trades across the day', () => {
    const { data, domain } = toTimeSeries([
      { date: '2026-10-01', cumulative_pnl: 10 },
      { date: '2026-10-01', cumulative_pnl: 5 },
      { date: '2026-10-11', cumulative_pnl: 20 },
    ])
    expect(data.map((p) => p.t)).toEqual([local(2026, 10, 1, 8), local(2026, 10, 1, 16), local(2026, 10, 11, 12)])
    expect(data.map((p) => p.n)).toEqual([1, 2, 3])
    expect(domain).toEqual([local(2026, 10, 1), local(2026, 10, 12)])
  })

  it('keeps day boundaries on local midnight across DST changes', () => {
    const [start, end] = dayBounds('2026-03-08')
    expect(new Date(start).getHours()).toBe(0)
    expect(new Date(end).getHours()).toBe(0)
    expect(new Date(end).getDate()).toBe(9)
  })
})

describe('timeTicks', () => {
  it('uses daily ticks for short spans', () => {
    const { ticks, unit } = timeTicks(local(2026, 10, 1), local(2026, 10, 5))
    expect(unit).toBe('day')
    expect(ticks).toHaveLength(5)
  })

  it('uses Monday ticks for a few months', () => {
    const { ticks, unit } = timeTicks(local(2026, 8, 1), local(2026, 10, 31))
    expect(unit).toBe('week')
    expect(ticks.every((t) => new Date(t).getDay() === 1)).toBe(true)
  })

  it('uses month starts for longer spans and labels the year when it changes', () => {
    const { ticks, unit } = timeTicks(local(2026, 3, 15), local(2027, 2, 10))
    expect(unit).toBe('month')
    expect(ticks.every((t) => new Date(t).getDate() === 1)).toBe(true)
    expect(formatTick(ticks[0], unit, true)).toBe('Apr 2026')
  })
})
