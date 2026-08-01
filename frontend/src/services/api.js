import axios from 'axios'
import { API_BASE_URL } from '@/constants'
import { getToken, removeToken } from '@/utils/token'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  // Let the browser set the correct multipart/form-data boundary when
  // the payload is a FormData (e.g. profile image upload). Keeping the
  // global application/json default here would make the server ignore
  // the file field entirely.
  if (typeof FormData !== 'undefined' && config.data instanceof FormData) {
    delete config.headers['Content-Type']
    delete config.headers['content-type']
  }
  return config
})

// On 401, clear the stale session so the UI redirects to login.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && getToken()) {
      removeToken()
      window.dispatchEvent(new CustomEvent('auth:unauthorized'))
    }
    return Promise.reject(error)
  }
)

export default api
