import { fmtPct, fmtR, fmtSignedMoney, pnlClass } from '../lib/format.js'

export default function BreakdownTable({ rows, label, emptyLabel }) {
  if (!rows.length) return <p className="muted empty">No closed trades yet.</p>

  return (
    <div className="table-wrap">
      <table className="breakdown">
        <thead>
          <tr>
            <th>{label}</th>
            <th className="num">Trades</th>
            <th>Win rate</th>
            <th className="num">Total P&L</th>
            <th className="num">Avg R</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((g) => (
            <tr key={g.key ?? '__none'}>
              <td className={g.key ? 'tag' : 'muted'}>{g.key ?? emptyLabel}</td>
              <td className="num">{g.trades}</td>
              <td>
                <div className="winrate">
                  <span className="winrate-bar">
                    <span style={{ width: `${g.win_rate ?? 0}%` }} />
                  </span>
                  <span className="num">{fmtPct(g.win_rate)}</span>
                </div>
              </td>
              <td className={`num ${pnlClass(g.total_pnl)}`}>{fmtSignedMoney(g.total_pnl)}</td>
              <td className={`num ${pnlClass(g.avg_r)}`}>{fmtR(g.avg_r)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
