import { useEffect, useState, useCallback } from 'react'
import { Search, ChevronLeft, ChevronRight, Star, Package } from 'lucide-react'
import { api } from '../lib/api'

export default function Products() {
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [pagination, setPagination] = useState(null)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .getCategories()
      .then((res) => setCategories(res.data))
      .catch(console.error)
  }, [])

  const fetchProducts = useCallback(() => {
    setLoading(true)
    api
      .getProducts(page, search, categoryId)
      .then((res) => {
        setProducts(res.data)
        setPagination(res.pagination)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [page, search, categoryId])

  useEffect(() => {
    fetchProducts()
  }, [fetchProducts])

  const handleSearch = (e) => {
    e.preventDefault()
    setPage(1)
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Products</h1>
          <p className="text-sm text-gray-500 mt-1">
            {pagination ? `${pagination.total} total products` : 'Loading...'}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={categoryId}
            onChange={(e) => {
              setCategoryId(e.target.value)
              setPage(1)
            }}
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">All Categories</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
          <form onSubmit={handleSearch} className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search products..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent w-60"
            />
          </form>
        </div>
      </div>

      {/* Product grid */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600" />
        </div>
      ) : products.length === 0 ? (
        <div className="text-center py-20 text-gray-400">No products found</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {products.map((p) => (
            <div
              key={p.id}
              className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow"
            >
              {p.primary_image_url ? (
                <img
                  src={p.primary_image_url}
                  alt={p.name}
                  className="w-full h-44 object-cover"
                />
              ) : (
                <div className="w-full h-44 bg-gray-100 flex items-center justify-center">
                  <Package className="w-10 h-10 text-gray-300" />
                </div>
              )}
              <div className="p-4 space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="text-sm font-semibold text-gray-900 line-clamp-1">
                    {p.name}
                  </h3>
                  {p.is_featured && (
                    <span className="shrink-0 inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-indigo-50 text-indigo-700">
                      Featured
                    </span>
                  )}
                </div>

                <p className="text-xs text-gray-500">{p.category_name}</p>

                <div className="flex items-center justify-between">
                  <span className="text-lg font-bold text-gray-900">
                    ${Number(p.base_price).toFixed(2)}
                  </span>
                  <div className="flex items-center gap-1 text-xs text-gray-500">
                    <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
                    {Number(p.avg_rating).toFixed(1)} ({p.review_count})
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-gray-500 pt-1 border-t border-gray-50">
                  <span>{p.variant_count} variants</span>
                  <span
                    className={
                      p.total_stock > 0 ? 'text-green-600' : 'text-red-500 font-medium'
                    }
                  >
                    {p.total_stock > 0 ? `${p.total_stock} in stock` : 'Out of stock'}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {pagination && pagination.total_pages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-500">
            Page {pagination.page} of {pagination.total_pages}
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-2 rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-white transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage((p) => Math.min(pagination.total_pages, p + 1))}
              disabled={page >= pagination.total_pages}
              className="p-2 rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-white transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
