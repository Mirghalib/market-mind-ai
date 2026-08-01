import api from './api'

/**
 * Admin endpoints — require the admin role. The axios interceptor
 * attaches the Bearer token automatically.
 */
export const adminService = {
  /** GET /admin/dashboard — platform-wide aggregates. */
  getStats: () => api.get('/admin/dashboard'),

  /** GET /admin/users — all users with search/filter/pagination. */
  getUsers: (params) => api.get('/admin/users', { params }),

  /** GET /admin/users/{id} — a single user with aggregates. */
  getUser: (id) => api.get(`/admin/users/${id}`),

  /** POST /admin/users — create a user directly. */
  createUser: (payload) => api.post('/admin/users', payload),

  /** PATCH /admin/users/{id} — edit name/role/status/verification. */
  updateUser: (id, payload) => api.patch(`/admin/users/${id}`, payload),

  /** POST /admin/users/{id}/reset-password */
  resetPassword: (id, payload) => api.post(`/admin/users/${id}/reset-password`, payload),

  /** POST /admin/users/{id}/verify-email */
  verifyEmail: (id) => api.post(`/admin/users/${id}/verify-email`),

  /** DELETE /admin/users/{id} — soft delete. */
  deleteUser: (id) => api.delete(`/admin/users/${id}`),

  /** POST /admin/users/{id}/restore */
  restoreUser: (id) => api.post(`/admin/users/${id}/restore`),

  /** GET /admin/roles — available roles for forms. */
  getRoles: () => api.get('/admin/roles'),

  /** POST /admin/invitations — invite a user by email. */
  inviteUser: (payload) => api.post('/admin/invitations', payload),

  /** GET /admin/invitations — list invitations. */
  getInvitations: () => api.get('/admin/invitations'),

  /** DELETE /admin/invitations/{id} — revoke an invitation. */
  revokeInvitation: (id) => api.delete(`/admin/invitations/${id}`),

  /** GET /admin/strategies — all strategies. */
  getStrategies: () => api.get('/admin/strategies'),

  /** GET /admin/exports — all exports across users (search/filter/sort/pagination). */
  getExports: (params) => api.get('/admin/exports', { params }),

  /** GET /admin/exports/{id}/download — download any export (blob). */
  downloadExport: (id) => api.get(`/admin/exports/${id}/download`, { responseType: 'blob' }),

  /** DELETE /admin/exports/{id} — permanently delete an export. */
  deleteExport: (id) => api.delete(`/admin/exports/${id}`),

  /** GET /admin/analytics — full platform analytics (stats, charts, activity). */
  getAnalytics: () => api.get('/admin/analytics'),

  /** DELETE /admin/user/{id} (legacy route kept for compatibility) */
  deleteUserLegacy: (id) => api.delete(`/admin/user/${id}`),

  /** DELETE /admin/strategy/{id} */
  deleteStrategy: (id) => api.delete(`/admin/strategy/${id}`),
}

export default adminService
