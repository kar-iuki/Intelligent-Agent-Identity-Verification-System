import { reactive, readonly } from 'vue'
import api from '../services/api.js'
import { setAuthToken, getAuthToken } from '../utils/authToken.js'
import supabase from '../services/supabase.js'

const state = reactive({
  user: JSON.parse(localStorage.getItem('auth_user') || 'null'),
  agent: JSON.parse(localStorage.getItem('auth_agent') || 'null'),
  token: getAuthToken(),
  role: localStorage.getItem('auth_role') || null,
  loading: false,
  error: null,
})

function persistSession(token, user, role, agent = null) {
  state.token = token
  state.user = user
  state.role = role
  state.agent = agent
  setAuthToken(token)

  if (user) {
    localStorage.setItem('auth_user', JSON.stringify(user))
  } else {
    localStorage.removeItem('auth_user')
  }

  if (role) {
    localStorage.setItem('auth_role', role)
  } else {
    localStorage.removeItem('auth_role')
  }

  if (agent) {
    localStorage.setItem('auth_agent', JSON.stringify(agent))
  } else {
    localStorage.removeItem('auth_agent')
  }
}

function clearSession() {
  state.token = null
  state.user = null
  state.agent = null
  state.role = null
  setAuthToken(null)
  localStorage.removeItem('auth_user')
  localStorage.removeItem('auth_role')
  localStorage.removeItem('auth_agent')
}

function getDashboardRoute(role) {
  return role === 'admin' ? '/admin/dashboard' : '/agent/dashboard'
}

export function useAuthStore() {
  async function login(email, password) {
    state.loading = true
    state.error = null

    try {
      const { data } = await api.post('/api/auth/login', { email, password })
      persistSession(data.token, data.user, data.role, data.agent)
      return data
    } catch (err) {
      state.error = err.response?.data?.error || 'Login failed'
      throw err
    } finally {
      state.loading = false
    }
  }

  async function register(formData) {
    state.loading = true
    state.error = null

    try {
      const { data } = await api.post('/api/auth/register', {
        fullName: formData.fullName,
        email: formData.email,
        password: formData.password,
        phoneNumber: formData.phoneNumber,
        nationalID: formData.nationalID,
      })
      return data
    } catch (err) {
      state.error = err.response?.data?.error || 'Registration failed'
      throw err
    } finally {
      state.loading = false
    }
  }

  async function logout() {
    try {
      if (state.token) {
        await api.post('/api/auth/logout')
      }
    } catch {
      // Clear local session even if server logout fails
    } finally {
      await supabase.auth.signOut()
      clearSession()
    }
  }

  async function fetchCurrentUser() {
    if (!state.token) return null

    state.loading = true
    state.error = null

    try {
      const { data } = await api.get('/api/auth/me')

      if (data.needsProfile) {
        if (data.email) {
          localStorage.setItem('oauth_email', data.email)
        }
        return data
      }

      persistSession(state.token, data.user, data.role, data.agent)
      return data
    } catch (err) {
      clearSession()
      state.error = err.response?.data?.error || 'Failed to fetch user'
      throw err
    } finally {
      state.loading = false
    }
  }

  async function completeProfile(formData) {
    state.loading = true
    state.error = null

    try {
      const { data } = await api.post('/api/auth/complete-profile', {
        fullName: formData.fullName,
        phoneNumber: formData.phoneNumber,
        nationalID: formData.nationalID,
      })
      persistSession(state.token, data.user, data.role, data.agent)
      return data
    } catch (err) {
      state.error = err.response?.data?.error || 'Failed to complete profile'
      throw err
    } finally {
      state.loading = false
    }
  }

  async function loginWithOAuth(provider) {
    const { error } = await supabase.auth.signInWithOAuth({
      provider,
      options: {
        redirectTo: `${window.location.origin}/login`,
      },
    })

    if (error) {
      state.error = error.message
      throw error
    }
  }

  async function handleOAuthCallback() {
    const { data: { session }, error } = await supabase.auth.getSession()

    if (error || !session) return null

    persistSession(session.access_token, null, null)

    try {
      return await fetchCurrentUser()
    } catch {
      clearSession()
      return null
    }
  }

  function isAuthenticated() {
    return !!state.token
  }

  return {
    state: readonly(state),
    login,
    register,
    logout,
    fetchCurrentUser,
    completeProfile,
    loginWithOAuth,
    handleOAuthCallback,
    isAuthenticated,
    getDashboardRoute,
    clearSession,
  }
}
