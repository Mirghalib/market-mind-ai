import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { authService, normalizeAuthResponse } from '@/services/auth'
import { setToken, getToken, removeToken } from '@/utils/token'
import { TOKEN_STORAGE_KEY } from '@/constants'

const USER_STORAGE_KEY = 'market_mind_ai_user'

export const AuthContext = createContext(null)

function getInitialState() {
  const token = getToken()
  if (!token) return { token: null, user: null }

  try {
    const stored = window.localStorage.getItem(USER_STORAGE_KEY)
    const user = stored ? JSON.parse(stored) : null
    return { token, user }
  } catch {
    return { token, user: null }
  }
}

export default function AuthProvider({ children }) {
  const [state, setState] = useState(getInitialState)

  // Keep stored user in sync with the token key.
  useEffect(() => {
    if (!state.token) return
    if (!state.user) {
      const { user } = normalizeAuthResponse({ access_token: state.token })
      setState((current) => ({ ...current, user }))
    }
    window.localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(state.user))
  }, [state.token, state.user])

  // A 401 from any API request (e.g. expired token) clears the session.
  useEffect(() => {
    const onUnauthorized = () => {
      removeToken()
      window.localStorage.removeItem(USER_STORAGE_KEY)
      setState({ token: null, user: null })
    }
    window.addEventListener('auth:unauthorized', onUnauthorized)
    return () => window.removeEventListener('auth:unauthorized', onUnauthorized)
  }, [])

  const login = useCallback(async (credentials) => {
    const { data } = await authService.login(credentials)
    const { token, user } = normalizeAuthResponse(data)
    if (!token) throw new Error('No token received from server')
    setToken(token)
    setState({ token, user })
    return user
  }, [])

  const register = useCallback(async (formData) => {
    const { data } = await authService.register(formData)
    // Registration returns the public profile (no token). Log the new
    // user in by calling the login endpoint with the same credentials.
    const { data: loginData } = await authService.login({
      email: formData.email,
      password: formData.password,
    })
    const { token, user } = normalizeAuthResponse({
      ...loginData,
      user: data,
    })
    if (!token) throw new Error('No token received from server')
    setToken(token)
    setState({ token, user })
    return user
  }, [])

  const logout = useCallback(async () => {
    try {
      await authService.logout()
    } catch {
      // The backend is stateless JWT auth — the endpoint may not exist;
      // always clear the local session.
    }
    removeToken()
    window.localStorage.removeItem(USER_STORAGE_KEY)
    setState({ token: null, user: null })
  }, [])

  const updateUser = useCallback((patch) => {
    setState((current) => {
      const next = {
        ...current,
        user: current.user ? { ...current.user, ...patch } : current.user,
      }
      window.localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(next.user))
      return next
    })
  }, [])

  const value = useMemo(
    () => ({
      ...state,
      isAuthenticated: Boolean(state.token),
      role: state.user?.role ?? null,
      userName: state.user?.name ?? null,
      login,
      register,
      logout,
      updateUser,
    }),
    [state, login, register, logout, updateUser]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
