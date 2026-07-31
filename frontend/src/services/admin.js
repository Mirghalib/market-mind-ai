import api from './api'

/**
 * Admin endpoints — require the admin role. The axios interceptor
 * attaches the Bearer token automatically.
 */
export const adminService = {
  /** GET /admin/dashboard — platform-wide aggregates. */
  getStats: () => api.get('/admin/dashboard'),

  /** GET /admin/users — all users. */
  getUsers: () => api.get('/admin/users'),

  /** GET /admin/strategies — all strategies. */
  getStrategies: () => api.get('/admin/strategies'),

  /** GET /admin/analytics — generation/export aggregates. */
  getAnalytics: () => api.get('/admin/analytics'),

  /** DELETE /admin/user/{id} */
  deleteUser: (id) => api.delete(`/admin/user/${id}`),

  /** DELETE /admin/strategy/{id} */
  deleteStrategy: (id) => api.delete(`/admin/strategy/${id}`),
}

export default adminService
