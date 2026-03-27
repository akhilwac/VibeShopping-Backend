import { useEffect, useState } from 'react'
import {
  Users,
  ShoppingCart,
  Package,
  DollarSign,
  Star,
  Clock,
  CheckCircle,
  XCircle,
} from 'lucide-react'
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { api } from '../lib/api'

const COLORS = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899']

function StatCard({ icon: Icon, label, value, color, sub }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500 font-medium">{label}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
        </div>
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [revenue, setRevenue] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.getDashboard(), api.getRevenue()])
      .then(([dashRes, revRes]) => {
        setStats(dashRes.data)
        setRevenue(revRes.data)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600" />
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        Failed to load dashboard data.
      </div>
    )
  }

  const orderStatusData = revenue?.orders_by_status
    ? Object.entries(revenue.orders_by_status).map(([name, value]) => ({ name, value }))
    : []

  const categoryData = revenue?.revenue_by_category
    ? Object.entries(revenue.revenue_by_category).map(([name, value]) => ({
        name,
        revenue: value,
      }))
    : []

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">Overview of your store performance</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={DollarSign}
          label="Total Revenue"
          value={`$${Number(stats.total_revenue).toLocaleString('en-US', { minimumFractionDigits: 2 })}`}
          color="bg-green-500"
        />
        <StatCard
          icon={ShoppingCart}
          label="Total Orders"
          value={stats.total_orders}
          color="bg-indigo-500"
          sub={`${stats.pending_orders} pending`}
        />
        <StatCard
          icon={Users}
          label="Total Users"
          value={stats.total_users}
          color="bg-blue-500"
          sub={`${stats.active_users} active`}
        />
        <StatCard
          icon={Package}
          label="Products"
          value={stats.total_products}
          color="bg-amber-500"
        />
      </div>

      {/* Second row stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Star} label="Reviews" value={stats.total_reviews} color="bg-purple-500" />
        <StatCard icon={Clock} label="Pending Orders" value={stats.pending_orders} color="bg-yellow-500" />
        <StatCard icon={CheckCircle} label="Delivered" value={stats.delivered_orders} color="bg-emerald-500" />
        <StatCard icon={XCircle} label="Cancelled" value={stats.cancelled_orders} color="bg-red-500" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Order status pie chart */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Orders by Status</h2>
          {orderStatusData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={orderStatusData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  dataKey="value"
                >
                  {orderStatusData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[300px] text-gray-400">
              No order data yet
            </div>
          )}
        </div>

        {/* Revenue by category bar chart */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Revenue by Category</h2>
          {categoryData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={categoryData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip formatter={(val) => `$${val.toFixed(2)}`} />
                <Bar dataKey="revenue" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[300px] text-gray-400">
              No revenue data yet
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
