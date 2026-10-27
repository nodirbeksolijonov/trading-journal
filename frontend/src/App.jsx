import { Link, NavLink, Navigate, Route, Routes } from 'react-router-dom'
import Dashboard from './pages/Dashboard.jsx'
import Trades from './pages/Trades.jsx'
import TradeForm from './pages/TradeForm.jsx'

export default function App() {
  return (
    <>
      <header className="topbar">
        <Link to="/" className="brand">Trading Journal</Link>
        <nav>
          <NavLink to="/" end>Dashboard</NavLink>
          <NavLink to="/trades" end>Trades</NavLink>
        </nav>
        <Link to="/trades/new" className="btn btn-primary">+ New trade</Link>
      </header>
      <main className="container">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/trades" element={<Trades />} />
          <Route path="/trades/new" element={<TradeForm />} />
          <Route path="/trades/:id/edit" element={<TradeForm />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </>
  )
}
