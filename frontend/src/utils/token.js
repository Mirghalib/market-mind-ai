import { TOKEN_STORAGE_KEY } from '@/constants'

export function getToken() {
  return localStorage.getItem(TOKEN_STORAGE_KEY)
}

export function setToken(token) {
  localStorage.setItem(TOKEN_STORAGE_KEY, token)
}

export function removeToken() {
  localStorage.removeItem(TOKEN_STORAGE_KEY)
}
