import { Area, AreaChart, CartesianGrid, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { fmtMoney, fmtShortDate, fmtSignedMoney, pnlClass } from '../lib/format.js'
import { formatTick, timeTicks, toTimeSeries } from '../lib/timeScale.js'

function ChartTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const p = payload[0].payload
  return (
    <div className="chart-tooltip">
      <div className="muted">{fmtShortDate(p.date, true)} · Trade #{p.n} · {p.symbol}</div>
      <div className={pnlClass(p.pnl)}>{fmtSignedMoney(p.pnl)}</div>
      <div>Equity {fmtMoney(p.cumulative_pnl)}</div>
    </div>
  )
}

export default function EquityChart({ points }) {
  if (!points.length) return <p className="muted empty">No closed trades yet.</p>

  // x is a timestamp, so gaps between trades show up as real distance on the axis.
  const { data, domain } = toTimeSeries(points)
  const { ticks, unit } = timeTicks(...domain)
  const spansYears = points[0].date.slice(0, 4) !== points.at(-1).date.slice(0, 4)

  return (
    <ResponsiveContainer width="100%" height={280}>
      <AreaChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: 8 }}>
        <defs>
          <linearGradient id="equityFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--accent)" stopOpacity={0.35} />
            <stop offset="100%" stopColor="var(--accent)" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="var(--border)" vertical={false} />
        <XAxis
          dataKey="t"
          type="number"
          scale="time"
          domain={domain}
          ticks={ticks}
          tickFormatter={(ms) => formatTick(ms, unit, spansYears)}
          minTickGap={24}
          stroke="var(--muted)"
          tickLine={false}
          axisLine={false}
          fontSize={12}
        />
        <YAxis
          stroke="var(--muted)"
          tickLine={false}
          axisLine={false}
          fontSize={12}
          width={70}
          tickFormatter={(v) => fmtMoney(v).replace(/\.\d+$/, '')}
        />
        <ReferenceLine y={0} stroke="var(--muted)" strokeDasharray="3 3" />
        <Tooltip content={<ChartTooltip />} cursor={{ stroke: 'var(--muted)' }} />
        <Area
          type="monotone"
          dataKey="cumulative_pnl"
          stroke="var(--accent)"
          strokeWidth={2}
          fill="url(#equityFill)"
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
