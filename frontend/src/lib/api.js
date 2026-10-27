const BASE = '/api'

// FastAPI validation errors arrive as [{loc, msg}, ...]; turn them into readable lines.
function formatDetail(detail) {
  if (!detail) return 'Request failed'
  if (typeof detail === 'string') return detail
  return detail
    .map((d) => {
      const field = d.loc?.filter((p) => p !== 'body').join('.')
      const msg = d.msg.replace(/^Value error, /, '')
      return field ? `${field.replaceAll('_', ' ')}: ${msg}` : msg
    })
    .join('\n')
}

function query(params = {}) {
  const clean = Object.entries(params).filter(([, v]) => v != null && v !== '')
  return clean.length ? `?${new URLSearchParams(clean)}` : ''
}

async function request(path, options = {}) {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (res.status === 204) return null
  const body = await res.json().catch(() => null)
  if (!res.ok) throw new Error(formatDetail(body?.detail))
  return body
}

export const api = {
  listTrades: (params) => request(`/trades${query(params)}`),
  getTrade: (id) => request(`/trades/${id}`),
  createTrade: (data) => request('/trades', { method: 'POST', body: JSON.stringify(data) }),
  updateTrade: (id, data) => request(`/trades/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteTrade: (id) => request(`/trades/${id}`, { method: 'DELETE' }),
  getStats: (params) => request(`/stats${query(params)}`),
}
