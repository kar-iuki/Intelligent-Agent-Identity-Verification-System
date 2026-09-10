import axios from 'axios'
import { getAuthToken, clearAuthToken } from '../utils/authToken.js'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:3000',
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = getAuthToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
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
