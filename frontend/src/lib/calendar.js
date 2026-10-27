const pad = (n) => String(n).padStart(2, '0')

// month is 0-based, like Date#getMonth.
export const isoDate = (year, month, day) => `${year}-${pad(month + 1)}-${pad(day)}`

export function todayIso() {
  const d = new Date()
  return isoDate(d.getFullYear(), d.getMonth(), d.getDate())
}

// Weeks start on Monday; days outside the month are null.
export function buildMonthGrid(year, month) {
  const offset = (new Date(year, month, 1).getDay() + 6) % 7
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const cells = Array(offset).fill(null)
  for (let day = 1; day <= daysInMonth; day++) cells.push(isoDate(year, month, day))
  while (cells.length % 7) cells.push(null)

  const weeks = []
  for (let i = 0; i < cells.length; i += 7) weeks.push(cells.slice(i, i + 7))
  return weeks
}
