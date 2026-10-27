const money = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })

export const fmtMoney = (v) => (v == null ? '—' : money.format(v))
export const fmtSignedMoney = (v) => (v == null ? '—' : (v > 0 ? '+' : '') + money.format(v))
export const fmtR = (v) => (v == null ? '—' : `${v > 0 ? '+' : ''}${v.toFixed(2)}R`)
export const fmtPct = (v) => (v == null ? '—' : `${v.toFixed(1)}%`)
export const fmtNumber = (v) =>
  v == null ? '—' : v.toLocaleString('en-US', { maximumFractionDigits: 8 })

export const pnlClass = (v) => (v == null || v === 0 ? '' : v > 0 ? 'pos' : 'neg')
