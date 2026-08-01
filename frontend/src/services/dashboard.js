import api from './api'

/**
 * User dashboard endpoints — all require the Bearer token, which the
 * axios interceptor attaches automatically.
 */
export const dashboardService = {
  /** GET /dashboard/dashboard — personal aggregates + latest strategy. */
  getStats: () => api.get('/dashboard/dashboard'),

  /** POST /dashboard/generate — run the AI marketing strategy pipeline. */
  generate: (payload) => api.post('/dashboard/generate', payload),

  /** GET /dashboard/history — paginated generation history. */
  getHistory: (params) => api.get('/dashboard/history', { params }),

  /** DELETE /generation-history/{id} — remove a history record. */
  deleteHistory: (id) => api.delete(`/generation-history/${id}`),

  /** POST /dashboard/export — download a strategy file (binary blob). */
  exportFile: (payload) => api.post('/dashboard/export', payload, { responseType: 'blob' }),

  /** GET /dashboard/exports — the current user's saved exports. */
  getExports: (params) => api.get('/dashboard/exports', { params }),

  /** GET /export/{id} — re-download a previously saved export (blob). */
  downloadExport: (id) => api.get(`/export/${id}`, { responseType: 'blob' }),

  /** POST /export/{id}/email — email a report link to a recipient. */
  emailExport: (id, payload) => api.post(`/export/${id}/email`, payload),

  /** POST /export/{id}/share — create a secure share link. */
  shareExport: (id, params) => api.post(`/export/${id}/share`, null, { params }),

  /** GET /export/{id}/shares — list share links for an export. */
  getShares: (id) => api.get(`/export/${id}/shares`),

  /** DELETE /export/{id}/shares/{shareId} — revoke a share link. */
  revokeShare: (id, shareId) => api.delete(`/export/${id}/shares/${shareId}`),
}

export default dashboardService
