const BASE = '/api/v1';

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
  return res.json();
}

export const api = {
  // Dashboard
  getDashboard: () => request('/admin/dashboard'),
  getRevenue: () => request('/admin/revenue'),

  // Users
  getUsers: (page = 1, search = '') =>
    request(`/admin/users?page=${page}&page_size=20${search ? `&search=${encodeURIComponent(search)}` : ''}`),
  toggleUserActive: (userId) =>
    request(`/admin/users/${userId}/toggle-active`, { method: 'PATCH' }),

  // Orders
  getOrders: (page = 1, status = '') =>
    request(`/admin/orders?page=${page}&page_size=20${status ? `&status=${status}` : ''}`),

  // Products
  getProducts: (page = 1, search = '', categoryId = '') =>
    request(`/admin/products?page=${page}&page_size=50${search ? `&search=${encodeURIComponent(search)}` : ''}${categoryId ? `&category_id=${categoryId}` : ''}`),

  // Categories
  getCategories: () => request('/categories'),
};
