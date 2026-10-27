const money = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })

// Round to cents before choosing a sign, so float noise like -0.001 shows as $0.00, not -$0.00.
// Adding 0 turns -0 into 0.
const toCents = (v) => Math.round(v * 100) / 100 + 0

export const fmtMoney = (v) => (v == null ? '—' : money.format(toCents(v)))
export const fmtSignedMoney = (v) => {
  if (v == null) return '—'
  const c = toCents(v)
  return (c > 0 ? '+' : '') + money.format(c)
}
export const fmtR = (v) => {
  if (v == null) return '—'
  const c = toCents(v)
  return `${c > 0 ? '+' : ''}${c.toFixed(2)}R`
}
export const fmtPct = (v) => (v == null ? '—' : `${v.toFixed(1)}%`)
export const fmtNumber = (v) =>
  v == null ? '—' : v.toLocaleString('en-US', { maximumFractionDigits: 8 })

// "2026-10-03" -> "Oct 3" (or "Oct 3, 2026" with withYear). Parsed as a local date to avoid timezone shifts.
export const fmtShortDate = (iso, withYear = false) => {
  const [y, m, d] = iso.split('-').map(Number)
  return new Date(y, m - 1, d).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    ...(withYear && { year: 'numeric' }),
  })
}

export const pnlClass = (v) => {
  if (v == null) return ''
  const c = toCents(v)
  return c === 0 ? '' : c > 0 ? 'pos' : 'neg'
}
