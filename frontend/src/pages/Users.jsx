import { useEffect, useState, useCallback } from 'react'
import { Search, ChevronLeft, ChevronRight, UserCheck, UserX } from 'lucide-react'
import { api } from '../lib/api'

export default function Users() {
  const [users, setUsers] = useState([])
  const [pagination, setPagination] = useState(null)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  const fetchUsers = useCallback(() => {
    setLoading(true)
    api
      .getUsers(page, search)
      .then((res) => {
        setUsers(res.data)
        setPagination(res.pagination)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [page, search])

  useEffect(() => {
    fetchUsers()
  }, [fetchUsers])

  const handleSearch = (e) => {
    e.preventDefault()
    setPage(1)
  }

  const toggleActive = async (userId) => {
    try {
      await api.toggleUserActive(userId)
      fetchUsers()
    } catch (err) {
      console.error(err)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Users</h1>
          <p className="text-sm text-gray-500 mt-1">
            {pagination ? `${pagination.total} total users` : 'Loading...'}
          </p>
        </div>
        <form onSubmit={handleSearch} className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search users..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent w-64"
          />
        </form>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-100">
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                User
              </th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Provider
              </th>
              <th className="text-center px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Orders
              </th>
              <th className="text-center px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Reviews
              </th>
              <th className="text-center px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Joined
              </th>
              <th className="px-5 py-3" />
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {loading ? (
              <tr>
                <td colSpan={7} className="text-center py-12 text-gray-400">
                  Loading...
                </td>
              </tr>
            ) : users.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-12 text-gray-400">
                  No users found
                </td>
              </tr>
            ) : (
              users.map((u) => (
                <tr key={u.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-5 py-3.5">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{u.full_name}</p>
                      <p className="text-xs text-gray-500">{u.email}</p>
                    </div>
                  </td>
                  <td className="px-5 py-3.5">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700 capitalize">
                      {u.auth_provider}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-center text-sm text-gray-700">{u.order_count}</td>
                  <td className="px-5 py-3.5 text-center text-sm text-gray-700">{u.review_count}</td>
                  <td className="px-5 py-3.5 text-center">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        u.is_active
                          ? 'bg-green-50 text-green-700'
                          : 'bg-red-50 text-red-700'
                      }`}
                    >
                      {u.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-sm text-gray-500">
                    {new Date(u.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-5 py-3.5">
                    <button
                      onClick={() => toggleActive(u.id)}
                      className={`p-1.5 rounded-lg transition-colors ${
                        u.is_active
                          ? 'text-red-500 hover:bg-red-50'
                          : 'text-green-500 hover:bg-green-50'
                      }`}
                      title={u.is_active ? 'Deactivate user' : 'Activate user'}
                    >
                      {u.is_active ? <UserX className="w-4 h-4" /> : <UserCheck className="w-4 h-4" />}
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        {/* Pagination */}
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
