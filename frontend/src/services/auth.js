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
 *
 * The backend returns either:
 *   - POST /auth/login  -> { access_token, token_type }  (JWT claims: sub, email, role)
 *   - POST /auth/register -> UserRead  (id, email, full_name, role_name, profile_image)
 */
export function normalizeAuthResponse(payload = {}) {
  const token = payload.access_token || payload.token || null
  const decoded = token ? decodeJwt(token) : null

  // Prefer explicit user data (register response), fall back to JWT claims.
  const raw = payload.user || payload
  const role = raw.role_name ?? raw.role ?? decoded?.role ?? 'user'
  const name =
    raw.full_name ?? raw.name ?? decoded?.full_name ?? decoded?.name ?? 'User'

  return {
    token,
    user: {
      id: raw?.id ?? decoded?.sub ?? null,
      name,
      email: raw?.email ?? decoded?.email ?? '',
      role,
      profileImage: raw?.profile_image ?? null,
    },
  }
}

// Auth endpoints.
export const authService = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (data) => api.post('/auth/register', data),
  logout: () => api.post('/auth/logout'),
  validateInvite: (token) => api.get('/invitations/validate', { params: { token } }),
  acceptInvite: (data) => api.post('/invitations/accept', data),
}
