import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../lib/api.js'
import { todayIso } from '../lib/calendar.js'
import { fmtMoney, fmtR, fmtSignedMoney, pnlClass } from '../lib/format.js'
import { tradeMetrics } from '../lib/tradeMath.js'

const EMOTIONS = ['calm', 'confident', 'neutral', 'excited', 'anxious', 'fearful', 'fomo', 'greedy', 'frustrated', 'revenge']
const NUMBER_FIELDS = ['entry_price', 'exit_price', 'position_size', 'stop_loss', 'take_profit', 'fees']

const emptyForm = () => ({
  symbol: '',
  side: 'long',
  entry_price: '',
  exit_price: '',
  position_size: '',
  stop_loss: '',
  take_profit: '',
  fees: '',
  entry_date: todayIso(),
  exit_date: '',
  strategy: '',
  notes: '',
  emotion_before: '',
  emotion_after: '',
})

const num = (v) => (v === '' || v == null ? null : Number(v))

export default function TradeForm() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [form, setForm] = useState(emptyForm)
  const [strategies, setStrategies] = useState([])
  const [error, setError] = useState(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    api.listTrades().then((ts) => setStrategies([...new Set(ts.map((t) => t.strategy).filter(Boolean))]))
    if (!id) return
    api
      .getTrade(id)
      .then((t) => setForm(Object.fromEntries(Object.keys(emptyForm()).map((k) => [k, t[k] ?? '']))))
      .catch((e) => setError(e.message))
  }, [id])

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }))

  // Exit price and exit date go together: filling the price defaults the date to the entry day.
  const setExitPrice = (e) => {
    const value = e.target.value
    setForm((f) => ({
      ...f,
      exit_price: value,
      exit_date: value && !f.exit_date ? f.entry_date : f.exit_date,
    }))
  }

  const preview = tradeMetrics({
    side: form.side,
    entry: num(form.entry_price),
    exit: num(form.exit_price),
    size: num(form.position_size),
    stop: num(form.stop_loss),
    takeProfit: num(form.take_profit),
    fees: num(form.fees),
  })

  const submit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError(null)
    const payload = { ...form }
    for (const k of NUMBER_FIELDS) payload[k] = num(form[k])
    payload.fees ??= 0
    payload.exit_date = form.exit_date || null
    try {
      await (id ? api.updateTrade(id, payload) : api.createTrade(payload))
      navigate('/trades')
    } catch (err) {
      setError(err.message)
      setSaving(false)
    }
  }

  return (
    <>
      <h1>{id ? 'Edit trade' : 'New trade'}</h1>
      <form className="trade-form" onSubmit={submit}>
        <div className="card form-main">
          <div className="form-grid">
            <label>
              Symbol
              <input value={form.symbol} onChange={set('symbol')} required maxLength={20} placeholder="AAPL" />
            </label>
            <label>
              Side
              <div className="segmented">
                {['long', 'short'].map((s) => (
                  <button
                    type="button"
                    key={s}
                    className={form.side === s ? `active ${s}` : ''}
                    onClick={() => setForm((f) => ({ ...f, side: s }))}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </label>
            <label>
              Position size
              <input type="number" step="any" min="0" value={form.position_size} onChange={set('position_size')} required />
            </label>
            <label>
              Entry date
              <input type="date" value={form.entry_date} onChange={set('entry_date')} required />
            </label>
            <label>
              Entry price
              <input type="number" step="any" min="0" value={form.entry_price} onChange={set('entry_price')} required />
            </label>
            <label>
              Exit date
              <input
                type="date"
                value={form.exit_date}
                onChange={set('exit_date')}
                min={form.entry_date}
                required={form.exit_price !== ''}
              />
            </label>
            <label>
              Exit price <span className="hint">empty = open</span>
              <input type="number" step="any" min="0" value={form.exit_price} onChange={setExitPrice} />
            </label>
            <label>
              Stop loss
              <input type="number" step="any" min="0" value={form.stop_loss} onChange={set('stop_loss')} />
            </label>
            <label>
              Take profit
              <input type="number" step="any" min="0" value={form.take_profit} onChange={set('take_profit')} />
            </label>
            <label>
              Fees <span className="hint">total, both sides</span>
              <input type="number" step="any" min="0" value={form.fees} onChange={set('fees')} placeholder="0" />
            </label>
            <label>
              Strategy
              <input value={form.strategy} onChange={set('strategy')} list="strategies" maxLength={50} placeholder="breakout" />
              <datalist id="strategies">
                {strategies.map((s) => <option key={s} value={s} />)}
              </datalist>
            </label>
            <label>
              Emotion before
              <input value={form.emotion_before} onChange={set('emotion_before')} list="emotions" maxLength={30} />
            </label>
            <label>
              Emotion after
              <input value={form.emotion_after} onChange={set('emotion_after')} list="emotions" maxLength={30} />
            </label>
            <datalist id="emotions">
              {EMOTIONS.map((e) => <option key={e} value={e} />)}
            </datalist>
          </div>
          <label>
            Notes
            <textarea
              rows={5}
              value={form.notes}
              onChange={set('notes')}
              maxLength={5000}
              placeholder="Why did you take it? Did you follow your plan? What would you do differently?"
            />
          </label>
        </div>

        <aside className="card form-side">
          <h2>Preview</h2>
          <dl className="preview">
            <dt>Gross P&L</dt>
            <dd className={pnlClass(preview.grossPnl)}>{fmtSignedMoney(preview.grossPnl)}</dd>
            <dt>Fees</dt>
            <dd>{num(form.fees) ? `−${fmtMoney(num(form.fees))}` : fmtMoney(0)}</dd>
            <dt>Net P&L</dt>
            <dd className={pnlClass(preview.pnl)}>{fmtSignedMoney(preview.pnl)}</dd>
            <dt>R-multiple</dt>
            <dd className={pnlClass(preview.rMultiple)}>{fmtR(preview.rMultiple)}</dd>
            <dt>Risk</dt>
            <dd>{fmtMoney(preview.risk)}</dd>
            <dt>Planned R:R</dt>
            <dd>{preview.plannedRR == null ? '—' : `1 : ${preview.plannedRR.toFixed(2)}`}</dd>
          </dl>
          {error && <p className="error">{error}</p>}
          <div className="form-actions">
            <button type="button" className="btn btn-ghost" onClick={() => navigate(-1)}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving…' : id ? 'Save changes' : 'Add trade'}
            </button>
          </div>
        </aside>
      </form>
    </>
  )
}
