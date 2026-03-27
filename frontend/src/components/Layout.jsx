import { NavLink, Outlet } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  ShoppingCart,
  Package,
  Store,
} from 'lucide-react'

const nav = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/users', icon: Users, label: 'Users' },
  { to: '/orders', icon: ShoppingCart, label: 'Orders' },
  { to: '/products', icon: Package, label: 'Products' },
]

export default function Layout() {
  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 text-gray-300 flex flex-col shrink-0">
        <div className="flex items-center gap-2 px-6 py-5 border-b border-gray-800">
          <Store className="w-7 h-7 text-indigo-400" />
          <span className="text-lg font-bold text-white tracking-tight">
            VibeShopping
          </span>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          {nav.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-indigo-600 text-white'
                    : 'hover:bg-gray-800 hover:text-white'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="px-6 py-4 border-t border-gray-800 text-xs text-gray-500">
          Admin Dashboard v1.0
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto bg-gray-50">
        <Outlet />
      </main>
    </div>
  )
}
