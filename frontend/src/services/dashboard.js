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

  /** POST /dashboard/export — download a strategy file. */
  export: (payload) => api.post('/dashboard/export', payload),
}

export default dashboardService
