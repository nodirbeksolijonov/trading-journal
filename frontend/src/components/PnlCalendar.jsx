import { useMemo, useState } from 'react'
import { buildMonthGrid } from '../lib/calendar.js'
import { fmtSignedMoney, pnlClass } from '../lib/format.js'

const WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

function initialMonth(daily) {
  // Open on the month of the latest trade so the calendar is never empty by default.
  const last = daily.at(-1)?.date
  if (last) {
    const [y, m] = last.split('-').map(Number)
    return { year: y, month: m - 1 }
  }
  const now = new Date()
  return { year: now.getFullYear(), month: now.getMonth() }
}

export default function PnlCalendar({ daily }) {
  const [{ year, month }, setView] = useState(() => initialMonth(daily))
  const byDate = useMemo(() => new Map(daily.map((d) => [d.date, d])), [daily])

  const weeks = buildMonthGrid(year, month)
  const monthDays = weeks.flat().filter(Boolean).map((d) => byDate.get(d)).filter(Boolean)
  const monthTotal = monthDays.reduce((sum, d) => sum + d.pnl, 0)
  const maxAbs = Math.max(1, ...monthDays.map((d) => Math.abs(d.pnl)))

  const shift = (delta) => {
    const d = new Date(year, month + delta, 1)
    setView({ year: d.getFullYear(), month: d.getMonth() })
  }

  const title = new Date(year, month, 1).toLocaleString('en-US', { month: 'long', year: 'numeric' })

  return (
    <div>
      <div className="calendar-head">
        <button className="btn btn-ghost" onClick={() => shift(-1)} aria-label="Previous month">‹</button>
        <h3>{title}</h3>
        <button className="btn btn-ghost" onClick={() => shift(1)} aria-label="Next month">›</button>
        <span className={`calendar-total ${pnlClass(monthTotal)}`}>
          {monthDays.length ? fmtSignedMoney(monthTotal) : 'No trades'}
        </span>
      </div>
      <div className="calendar">
        {WEEKDAYS.map((w) => (
          <div key={w} className="calendar-weekday">{w}</div>
        ))}
        {weeks.flat().map((date, i) => {
          if (!date) return <div key={`pad-${i}`} className="calendar-cell pad" />
          const day = byDate.get(date)
          const tone = day ? pnlClass(day.pnl) : ''
          const alpha = day ? 0.12 + 0.5 * (Math.abs(day.pnl) / maxAbs) : 0
          return (
            <div key={date} className={`calendar-cell ${tone}`} style={{ '--alpha': alpha }}>
              <span className="calendar-day">{Number(date.slice(8))}</span>
              {day && (
                <>
                  <span className="calendar-pnl">{fmtSignedMoney(day.pnl)}</span>
                  <span className="calendar-count">
                    {day.trades} trade{day.trades > 1 ? 's' : ''}
                  </span>
                </>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
