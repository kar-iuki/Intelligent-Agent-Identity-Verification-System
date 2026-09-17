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
  async function register(formData) {
    state.loading = true
    state.error = null

    try {
      const { getDeviceFingerprint } = await import('../utils/deviceFingerprint.js')
      const { data } = await api.post('/api/auth/register', {
        fullName: formData.fullName,
        email: formData.email,
        password: formData.password,
        confirmPassword: formData.confirmPassword,
        deviceFingerprint: getDeviceFingerprint(),
      })

      if (data.token && data.needsProfile) {
        persistSession(data.token, null, null)
        if (data.email) localStorage.setItem('oauth_email', data.email)
        if (data.suggestedFullName) {
          localStorage.setItem('suggested_full_name', data.suggestedFullName)
        }
      }

      return data
    } catch (err) {
      state.error = err.response?.data?.error || 'Registration failed'
      throw err
    } finally {
      state.loading = false
    }
  }

  async function resendVerificationEmail(email) {
    const { data } = await api.post('/api/auth/resend-verification', { email })
    return data
  }

  async function login(email, password) {
    state.loading = true
    state.error = null

    try {
      const { data } = await api.post('/api/auth/login', { email, password })

      if (data.needsProfile && data.token) {
        persistSession(data.token, null, null)
        if (data.email) localStorage.setItem('oauth_email', data.email)
        if (data.suggestedFullName) {
          localStorage.setItem('suggested_full_name', data.suggestedFullName)
        }
        return data
      }

      persistSession(data.token, data.user, data.role, data.agent)
      return data
    } catch (err) {
      state.error = err.response?.data?.error || 'Login failed'
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
        if (data.suggestedFullName) {
          localStorage.setItem('suggested_full_name', data.suggestedFullName)
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
        dateOfBirth: formData.dateOfBirth,
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
    const redirectTo = `${window.location.origin}/login`
    // Must match the browser origin that receives ?code= (same device + same URL).
    localStorage.setItem('oauth_started_origin', window.location.origin)
    localStorage.setItem('oauth_redirect_to', redirectTo)
    state.error = null

    const { error } = await supabase.auth.signInWithOAuth({
      provider,
      options: {
        redirectTo,
        queryParams: {
          prompt: 'select_account',
        },
      },
    })

    if (error) {
      state.error = error.message
      throw error
    }
  }

  function clearOAuthUrlParams() {
    const url = new URL(window.location.href)
    if (!url.searchParams.has('code') && !url.searchParams.has('error')) return
    window.history.replaceState({}, '', url.pathname)
  }

  async function handleOAuthCallback() {
    const params = new URLSearchParams(window.location.search)
    const code = params.get('code')
    const oauthError = params.get('error_description') || params.get('error')

    if (oauthError) {
      state.error = oauthError
      clearOAuthUrlParams()
      return null
    }

    // Not an OAuth return — leave existing sessions alone for normal login page loads
    if (!code) {
      return null
    }

    const startedOrigin = localStorage.getItem('oauth_started_origin')
    if (startedOrigin && startedOrigin !== window.location.origin) {
      state.error =
        `Google sent you back to ${window.location.origin}, but sign-in started on ${startedOrigin}. ` +
        'Open the app with one URL only (your ngrok https link), add that exact URL to Supabase Redirect URLs, then try Continue with Google again.'
      clearOAuthUrlParams()
      return null
    }

    const { data, error: exchangeError } = await supabase.auth.exchangeCodeForSession(code)
    clearOAuthUrlParams()
    localStorage.removeItem('oauth_started_origin')
    localStorage.removeItem('oauth_redirect_to')

    if (exchangeError) {
      const msg = exchangeError.message || ''
      if (/verifier|PKCE/i.test(msg)) {
        state.error =
          'Google sign-in could not finish (login session was lost). ' +
          'Use the same browser and the same ngrok URL for the whole flow — do not switch between localhost and ngrok. Tap Continue with Google again.'
      } else {
        state.error = msg
      }
      return null
    }

    const session = data?.session
    if (!session) {
      state.error = 'Google sign-in did not return a session. Please try again.'
      return null
    }

    persistSession(session.access_token, null, null)

    try {
      return await fetchCurrentUser()
    } catch (err) {
      state.error = err.response?.data?.error || err.message || 'Could not finish Google sign-in'
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
    resendVerificationEmail,
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
