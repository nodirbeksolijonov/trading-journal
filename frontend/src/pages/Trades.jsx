import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api.js'
import { fmtNumber, fmtR, fmtSignedMoney, pnlClass } from '../lib/format.js'

export default function Trades() {
  const [trades, setTrades] = useState(null)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({ symbol: '', strategy: '' })

  const load = useCallback(() => {
    api.listTrades(filters).then(setTrades).catch((e) => setError(e.message))
  }, [filters])

  useEffect(load, [load])

  const remove = async (trade) => {
    if (!confirm(`Delete ${trade.symbol} trade from ${trade.trade_date}?`)) return
    try {
      await api.deleteTrade(trade.id)
      load()
    } catch (e) {
      setError(e.message)
    }
  }

  const setFilter = (key) => (e) => setFilters((f) => ({ ...f, [key]: e.target.value }))

  return (
    <>
      <div className="page-head">
        <h1>Trades</h1>
        <div className="filters">
          <input placeholder="Symbol" value={filters.symbol} onChange={setFilter('symbol')} />
          <input placeholder="Strategy" value={filters.strategy} onChange={setFilter('strategy')} />
        </div>
      </div>

      {error && <p className="error">{error}</p>}
      {!trades ? (
        <p className="muted">Loading…</p>
      ) : trades.length === 0 ? (
        <div className="card empty-state">
          <p className="muted">No trades match.</p>
        </div>
      ) : (
        <div className="card table-wrap">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Symbol</th>
                <th>Side</th>
                <th className="num">Entry</th>
                <th className="num">Exit</th>
                <th className="num">Size</th>
                <th className="num">P&L</th>
                <th className="num">R</th>
                <th>Strategy</th>
                <th>Emotion</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {trades.map((t) => (
                <tr key={t.id}>
                  <td>{t.trade_date}</td>
                  <td className="symbol" title={t.notes ?? ''}>{t.symbol}</td>
                  <td><span className={`badge ${t.side}`}>{t.side}</span></td>
                  <td className="num">{fmtNumber(t.entry_price)}</td>
                  <td className="num">{t.exit_price == null ? <span className="badge">open</span> : fmtNumber(t.exit_price)}</td>
                  <td className="num">{fmtNumber(t.position_size)}</td>
                  <td className={`num ${pnlClass(t.pnl)}`}>{fmtSignedMoney(t.pnl)}</td>
                  <td className={`num ${pnlClass(t.r_multiple)}`}>{fmtR(t.r_multiple)}</td>
                  <td>{t.strategy ?? '—'}</td>
                  <td className="muted">{t.emotion_before ?? '—'} → {t.emotion_after ?? '—'}</td>
                  <td className="actions">
                    <Link to={`/trades/${t.id}/edit`} className="btn btn-ghost">Edit</Link>
                    <button className="btn btn-ghost danger" onClick={() => remove(t)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}
