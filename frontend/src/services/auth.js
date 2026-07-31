import api from './api'

/**
 * Decode the payload of a JWT without a verification library.
 * Returns null for malformed tokens. The signature is validated by
 * the backend on every request; here we only read role/name/exp.
 */
export function decodeJwt(token) {
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const json = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => `%${c.charCodeAt(0).toString(16).padStart(2, '0')}`)
        .join('')
    )
    return JSON.parse(json)
  } catch {
    return null
  }
}

/**
 * Map a raw API user/token payload to a normalized auth user.
 * Accepts both `{ token, user }` and a flat `{ access_token, ... }` shape.
 */
export function normalizeAuthResponse(payload = {}) {
  const token = payload.token || payload.access_token || null
  const raw = payload.user || payload
  const decoded = token ? decodeJwt(token) : null

  return {
    token,
    user: {
      id: raw?.id ?? decoded?.sub ?? null,
      name: raw?.name ?? decoded?.name ?? 'User',
      email: raw?.email ?? decoded?.email ?? '',
      role: raw?.role ?? decoded?.role ?? 'user',
    },
  }
}

// Auth endpoints.
export const authService = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (data) => api.post('/auth/register', data),
  logout: () => api.post('/auth/logout'),
}
