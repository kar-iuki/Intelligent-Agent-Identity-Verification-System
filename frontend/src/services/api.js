import axios from 'axios'
import { getAuthToken, clearAuthToken } from '../utils/authToken.js'

const api = axios.create({
  // Same-origin by default so Vite can proxy /api (works on phone via LAN IP).
  // Override with VITE_API_URL when the API is on a different host.
  baseURL: import.meta.env.VITE_API_URL || '',
})

api.interceptors.request.use((config) => {
  const token = getAuthToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  const isFormData = typeof FormData !== 'undefined' && config.data instanceof FormData

  if (isFormData) {
    // Must not force application/json — browser sets multipart boundary.
    if (typeof config.headers.set === 'function') {
      config.headers.set('Content-Type', undefined)
    } else {
      delete config.headers['Content-Type']
      delete config.headers['content-type']
    }
  } else if (config.data && typeof config.data === 'object' && !config.headers['Content-Type']) {
    config.headers['Content-Type'] = 'application/json'
  }

  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      clearAuthToken()
      localStorage.removeItem('auth_user')
      localStorage.removeItem('auth_role')
      localStorage.removeItem('auth_agent')

      const { default: router } = await import('../router')
      const currentRoute = router.currentRoute.value
      if (currentRoute.name !== 'login' && currentRoute.name !== 'register') {
        router.push('/login')
      }
    }
    return Promise.reject(error)
  }
)

export default api
