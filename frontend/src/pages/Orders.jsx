import { useEffect, useState, useCallback } from 'react'
import { ChevronLeft, ChevronRight, Filter } from 'lucide-react'
import { api } from '../lib/api'

const STATUS_STYLES = {
  pending: 'bg-yellow-50 text-yellow-700',
  confirmed: 'bg-blue-50 text-blue-700',
  shipped: 'bg-indigo-50 text-indigo-700',
  delivered: 'bg-green-50 text-green-700',
  cancelled: 'bg-red-50 text-red-700',
}

const STATUSES = ['', 'pending', 'confirmed', 'shipped', 'delivered', 'cancelled']

export default function Orders() {
  const [orders, setOrders] = useState([])
  const [pagination, setPagination] = useState(null)
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState('')
  const [loading, setLoading] = useState(true)

  const fetchOrders = useCallback(() => {
    setLoading(true)
    api
      .getOrders(page, statusFilter)
      .then((res) => {
        setOrders(res.data)
        setPagination(res.pagination)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [page, statusFilter])

  useEffect(() => {
    fetchOrders()
  }, [fetchOrders])

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Orders</h1>
          <p className="text-sm text-gray-500 mt-1">
            {pagination ? `${pagination.total} total orders` : 'Loading...'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value)
              setPage(1)
            }}
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s || 'All Statuses'}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-100">
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Order ID
              </th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Customer
              </th>
              <th className="text-center px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Items
              </th>
              <th className="text-right px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Total
              </th>
              <th className="text-center px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Date
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {loading ? (
              <tr>
                <td colSpan={6} className="text-center py-12 text-gray-400">
                  Loading...
                </td>
              </tr>
            ) : orders.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center py-12 text-gray-400">
                  No orders found
                </td>
              </tr>
            ) : (
              orders.map((o) => (
                <tr key={o.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-5 py-3.5 text-sm font-mono text-gray-700">
                    {o.id.slice(0, 8)}...
                  </td>
                  <td className="px-5 py-3.5">
                    <p className="text-sm font-medium text-gray-900">{o.user_name}</p>
                    <p className="text-xs text-gray-500">{o.user_email}</p>
                  </td>
                  <td className="px-5 py-3.5 text-center text-sm text-gray-700">
                    {o.item_count}
                  </td>
                  <td className="px-5 py-3.5 text-right text-sm font-semibold text-gray-900">
                    ${Number(o.total).toFixed(2)}
                  </td>
                  <td className="px-5 py-3.5 text-center">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${
                        STATUS_STYLES[o.status] || 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {o.status}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-sm text-gray-500">
                    {new Date(o.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        {pagination && pagination.total_pages > 1 && (
          <div className="flex items-center justify-between px-5 py-3 border-t border-gray-100 bg-gray-50">
            <p className="text-sm text-gray-500">
              Page {pagination.page} of {pagination.total_pages}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-1.5 rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-white transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => setPage((p) => Math.min(pagination.total_pages, p + 1))}
                disabled={page >= pagination.total_pages}
                className="p-1.5 rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-white transition-colors"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
