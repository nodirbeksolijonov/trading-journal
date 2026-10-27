import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import EquityChart from '../components/EquityChart.jsx'
import PnlCalendar from '../components/PnlCalendar.jsx'
import StatCard from '../components/StatCard.jsx'
import { api } from '../lib/api.js'
import { fmtPct, fmtR, fmtSignedMoney, pnlClass } from '../lib/format.js'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.getStats().then(setStats).catch((e) => setError(e.message))
  }, [])

  if (error) return <p className="error">Could not load stats: {error}</p>
  if (!stats) return <p className="muted">Loading…</p>

  const s = stats.summary
  if (s.total_trades === 0) {
    return (
      <div className="card empty-state">
        <h2>No trades yet</h2>
        <p className="muted">Log your first trade to start seeing your stats.</p>
        <Link to="/trades/new" className="btn btn-primary">+ New trade</Link>
      </div>
    )
  }

  return (
    <>
      <h1>Dashboard</h1>
      <section className="stats-grid">
        <StatCard
          label="Win rate"
          value={fmtPct(s.win_rate)}
          sub={`${s.wins}W · ${s.losses}L · ${s.breakeven} BE`}
        />
        <StatCard label="Total P&L" value={fmtSignedMoney(s.total_pnl)} tone={pnlClass(s.total_pnl)} />
        <StatCard label="Average R" value={fmtR(s.avg_r)} tone={pnlClass(s.avg_r)} />
        <StatCard
          label="Trades"
          value={s.total_trades}
          sub={`${s.closed_trades} closed · ${s.open_trades} open`}
        />
      </section>

      <section className="card">
        <h2>Equity curve</h2>
        <EquityChart points={stats.equity_curve} />
      </section>

      <section className="card">
        <h2>P&L calendar</h2>
        <PnlCalendar daily={stats.daily_pnl} />
      </section>
    </>
  )
}
