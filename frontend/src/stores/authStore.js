import { reactive, readonly } from 'vue'
import api from '../services/api.js'
import { syncPasskeyHints } from '../services/passkeyService.js'
import { setAuthToken, getAuthToken } from '../utils/authToken.js'
import supabase from '../services/supabase.js'

// Keep auth usable when browser storage is blocked.
const safeStorage = {
  getItem(key) { try { return window.localStorage.getItem(key) } catch { return null } },
  setItem(key, value) { try { window.localStorage.setItem(key, value) } catch { /* Optional persistence. */ } },
  removeItem(key) { try { window.localStorage.removeItem(key) } catch { /* Optional persistence. */ } },
}

const state = reactive({
  user: JSON.parse(safeStorage.getItem('auth_user') || 'null'),
  agent: JSON.parse(safeStorage.getItem('auth_agent') || 'null'),
  token: getAuthToken(),
  role: safeStorage.getItem('auth_role') || null,
  loading: false,
  error: null,
  passkeyPromptEligible: false,
  passkeyPromptShown: false,
})

function persistSession(token, user, role, agent = null) {
  state.token = token
  state.user = user
  state.role = role
  state.agent = agent
  setAuthToken(token)

  if (user) {
    safeStorage.setItem('auth_user', JSON.stringify(user))
  } else {
    safeStorage.removeItem('auth_user')
  }

  if (role) {
    safeStorage.setItem('auth_role', role)
  } else {
    safeStorage.removeItem('auth_role')
  }

  if (agent) {
    safeStorage.setItem('auth_agent', JSON.stringify(agent))
  } else {
    safeStorage.removeItem('auth_agent')
  }
}

function clearSession() {
  state.passkeyPromptEligible = false
  state.passkeyPromptShown = false
  state.token = null
  state.user = null
  state.agent = null
  state.role = null
  setAuthToken(null)
  safeStorage.removeItem('auth_user')
  safeStorage.removeItem('auth_role')
  safeStorage.removeItem('auth_agent')
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
        if (data.email) safeStorage.setItem('oauth_email', data.email)
        if (data.suggestedFullName) {
          safeStorage.setItem('suggested_full_name', data.suggestedFullName)
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

  async function login(email, password, captcha = {}) {
    state.loading = true
    state.error = null

    try {
      const { data } = await api.post('/api/auth/login', {
        email: String(email || '').trim().toLowerCase(),
        password,
        captchaId: captcha.id,
        captchaAnswer: captcha.answer,
      })
      state.passkeyPromptEligible = true
      state.passkeyPromptShown = false

      if (data.needsProfile && data.token) {
        persistSession(data.token, null, null)
        if (data.email) safeStorage.setItem('oauth_email', data.email)
        if (data.suggestedFullName) {
          safeStorage.setItem('suggested_full_name', data.suggestedFullName)
        }
        return data
      }

      persistSession(data.token, data.user, data.role, data.agent)
      syncPasskeyHints().catch(() => {})
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
          safeStorage.setItem('oauth_email', data.email)
        }
        if (data.suggestedFullName) {
          safeStorage.setItem('suggested_full_name', data.suggestedFullName)
        }
        return data
      }

      persistSession(state.token, data.user, data.role, data.agent)
      syncPasskeyHints().catch(() => {})
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
      state.passkeyPromptEligible = true
      syncPasskeyHints().catch(() => {})
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
    safeStorage.setItem('oauth_started_origin', window.location.origin)
    safeStorage.setItem('oauth_redirect_to', redirectTo)
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

  const RECOVERY_KEY = 'recovery_access_token'

  function setRecoveryToken(token) {
    try { window.sessionStorage.setItem(RECOVERY_KEY, token) } catch { /* Optional persistence. */ }
  }

  function hasRecoverySession() {
    try { return !!window.sessionStorage.getItem(RECOVERY_KEY) } catch { return false }
  }

  function clearRecoveryToken() {
    try { window.sessionStorage.removeItem(RECOVERY_KEY) } catch { /* Optional persistence. */ }
  }

  function clearAuthRedirectFromUrl() {
    const url = new URL(window.location.href)
    for (const key of ['code', 'error', 'error_code', 'error_description', 'token_hash', 'type']) {
      url.searchParams.delete(key)
    }
    url.hash = ''
    const search = url.searchParams.toString()
    window.history.replaceState({}, '', url.pathname + (search ? `?${search}` : ''))
  }

  function redirectErrorMessage(query, hash) {
    const code = hash.get('error_code') || query.get('error_code')
    const raw = hash.get('error_description') || query.get('error_description') || hash.get('error') || query.get('error')
    if (!raw && !code) return ''
    if (code === 'otp_expired') {
      return 'This email link has expired. Request a new confirmation or password reset email.'
    }
    return raw || 'The email link could not be opened. Request a new one and try again.'
  }

  async function finishRedirectSession(accessToken) {
    persistSession(accessToken, null, null)
    try {
      const user = await fetchCurrentUser()
      state.passkeyPromptEligible = true
      state.passkeyPromptShown = false
      syncPasskeyHints().catch(() => {})
      return user
    } catch (err) {
      state.error = err.response?.data?.error || err.message || 'Could not finish sign-in from the email link'
      clearSession()
      return null
    }
  }

  async function handleOAuthCallback() {
    const query = new URLSearchParams(window.location.search)
    const hash = new URLSearchParams(window.location.hash.replace(/^#/, ''))
    const redirectError = redirectErrorMessage(query, hash)

    if (redirectError) {
      state.error = redirectError
      clearAuthRedirectFromUrl()
      return null
    }

    const accessToken = hash.get('access_token') || query.get('access_token')
    const type = (hash.get('type') || query.get('type') || '').toLowerCase()
    const tokenHash = query.get('token_hash') || hash.get('token_hash')

    if (accessToken) {
      clearAuthRedirectFromUrl()
      const openedResetLink = window.location.pathname === '/reset-password' && type !== 'signup' && type !== 'email'
      if (type === 'recovery' || openedResetLink) {
        setRecoveryToken(accessToken)
        return { recovery: true }
      }
      return finishRedirectSession(accessToken)
    }

    if (tokenHash && type) {
      const { data, error } = await supabase.auth.verifyOtp({ token_hash: tokenHash, type })
      clearAuthRedirectFromUrl()
      if (error || !data?.session) {
        state.error = error?.message || 'The email link could not be confirmed. Request a new one and try again.'
        return null
      }
      if (type === 'recovery') {
        setRecoveryToken(data.session.access_token)
        return { recovery: true }
      }
      return finishRedirectSession(data.session.access_token)
    }

    const code = query.get('code')
    if (!code) return null

    const startedOrigin = safeStorage.getItem('oauth_started_origin')
    if (startedOrigin && startedOrigin !== window.location.origin) {
      state.error =
        `Google sent you back to ${window.location.origin}, but sign-in started on ${startedOrigin}. ` +
        'Open the app with one URL only (your ngrok https link), add that exact URL to Supabase Redirect URLs, then try Continue with Google again.'
      clearAuthRedirectFromUrl()
      return null
    }

    const { data, error: exchangeError } = await supabase.auth.exchangeCodeForSession(code)
    clearAuthRedirectFromUrl()
    safeStorage.removeItem('oauth_started_origin')
    safeStorage.removeItem('oauth_redirect_to')

    if (exchangeError) {
      const msg = exchangeError.message || ''
      if (/verifier|PKCE/i.test(msg)) {
        state.error = startedOrigin
          ? 'Google sign-in could not finish (login session was lost). ' +
            'Use the same browser and the same ngrok URL for the whole flow — do not switch between localhost and ngrok. Tap Continue with Google again.'
          : 'This email link could not be completed in this browser. Request a new confirmation or password reset email and open it here.'
      } else {
        state.error = msg
      }
      return null
    }

    const session = data?.session
    if (!session) {
      state.error = 'Sign-in did not return a session. Please try again.'
      return null
    }

    return finishRedirectSession(session.access_token)
  }

  async function forgotPassword(email) {
    const { data } = await api.post('/api/auth/forgot-password', { email: String(email || '').trim().toLowerCase() })
    return data
  }

  async function resetPassword(password) {
    let token = null
    try { token = window.sessionStorage.getItem(RECOVERY_KEY) } catch { token = null }
    if (!token) {
      const error = new Error('Open the reset link from your email, then choose a new password.')
      state.error = error.message
      throw error
    }

    state.loading = true
    state.error = null
    try {
      const { data } = await api.post('/api/auth/reset-password', { password }, {
        headers: { Authorization: `Bearer ${token}` },
      })
      clearRecoveryToken()

      if (data.needsProfile && data.token) {
        persistSession(data.token, null, null)
        if (data.email) safeStorage.setItem('oauth_email', data.email)
        if (data.suggestedFullName) safeStorage.setItem('suggested_full_name', data.suggestedFullName)
        return data
      }

      if (data.token && data.role) {
        persistSession(data.token, data.user, data.role, data.agent)
      }
      return data
    } catch (err) {
      state.error = err.response?.data?.error || 'Could not update your password'
      throw err
    } finally {
      state.loading = false
    }
  }

  function isAuthenticated() {
    return !!state.token
  }

  function acceptPasskeySession(data) {
    persistSession(data.token, data.user, data.role, data.agent)
    state.passkeyPromptEligible = false
    state.passkeyPromptShown = true
    syncPasskeyHints().catch(() => {})
  }

  function claimPasskeyPrompt() {
    if (state.passkeyPromptShown || !state.passkeyPromptEligible) return false
    state.passkeyPromptShown = true
    return true
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
    forgotPassword,
    resetPassword,
    hasRecoverySession,
    isAuthenticated,
    getDashboardRoute,
    clearSession,
    acceptPasskeySession,
    claimPasskeyPrompt,
  }
}
