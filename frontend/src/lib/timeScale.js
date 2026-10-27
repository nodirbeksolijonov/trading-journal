// Helpers for plotting trades on a real time axis. All dates are local, built with
// the Date(y, m, d) constructor so DST changes never shift a day boundary.

const DAY_MS = 86_400_000

export function dayBounds(iso) {
  const [y, m, d] = iso.split('-').map(Number)
  return [new Date(y, m - 1, d).getTime(), new Date(y, m - 1, d + 1).getTime()]
}

// Trades only have a date, so spread same-day trades evenly across that day:
// one trade sits at noon, two at 8:00 and 16:00, and so on.
export function toTimeSeries(points) {
  const perDay = new Map()
  for (const p of points) perDay.set(p.date, (perDay.get(p.date) ?? 0) + 1)

  const seen = new Map()
  const data = points.map((p, i) => {
    const k = (seen.get(p.date) ?? 0) + 1
    seen.set(p.date, k)
    const [start, end] = dayBounds(p.date)
    return { ...p, n: i + 1, t: start + ((end - start) * k) / (perDay.get(p.date) + 1) }
  })

  const domain = points.length
    ? [dayBounds(points[0].date)[0], dayBounds(points.at(-1).date)[1]]
    : [0, 0]
  return { data, domain }
}

// Ticks on calendar boundaries; the unit grows with the visible span.
export function timeTicks(min, max) {
  const days = (max - min) / DAY_MS
  const unit = days <= 16 ? 'day' : days <= 120 ? 'week' : days <= 730 ? 'month' : 'year'

  const first = new Date(min)
  let d = new Date(first.getFullYear(), first.getMonth(), first.getDate())
  if (unit === 'week') d.setDate(d.getDate() + ((8 - d.getDay()) % 7)) // next Monday
  if (unit === 'month' && d.getDate() !== 1) d = new Date(d.getFullYear(), d.getMonth() + 1, 1)
  if (unit === 'year' && d.getTime() !== new Date(d.getFullYear(), 0, 1).getTime())
    d = new Date(d.getFullYear() + 1, 0, 1)

  const ticks = []
  while (d.getTime() <= max) {
    if (d.getTime() >= min) ticks.push(d.getTime())
    if (unit === 'day') d = new Date(d.getFullYear(), d.getMonth(), d.getDate() + 1)
    else if (unit === 'week') d = new Date(d.getFullYear(), d.getMonth(), d.getDate() + 7)
    else if (unit === 'month') d = new Date(d.getFullYear(), d.getMonth() + 1, 1)
    else d = new Date(d.getFullYear() + 1, 0, 1)
  }
  return { ticks, unit }
}

export function formatTick(ms, unit, spansYears) {
  const d = new Date(ms)
  if (unit === 'year') return String(d.getFullYear())
  if (unit === 'month') {
    return d.toLocaleDateString('en-US', { month: 'short', ...(spansYears && { year: 'numeric' }) })
  }
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}
