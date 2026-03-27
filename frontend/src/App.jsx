import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Users from './pages/Users'
import Orders from './pages/Orders'
import Products from './pages/Products'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/users" element={<Users />} />
        <Route path="/orders" element={<Orders />} />
        <Route path="/products" element={<Products />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
