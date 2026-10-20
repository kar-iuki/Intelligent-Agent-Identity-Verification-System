<template>
  <div class="auth-page">
    <div class="auth-card">
      <p class="auth-eyebrow">WELCOME BACK</p>
      <h1>Sign in to your workspace</h1>
      <p class="subtitle">Continue your verification journey.</p>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            autocomplete="username webauthn"
            placeholder="you@example.com"
            required
          />
        </div>

        <div class="form-group">
          <div class="password-label">
            <label for="password">Password</label>
            <router-link to="/forgot-password">Forgot password?</router-link>
          </div>
          <input
            id="password"
            v-model="password"
            type="password"
            autocomplete="current-password"
            placeholder="Enter your password"
            required
          />
        </div>

        <div class="form-group">
          <label for="captcha">Human check</label>
          <div class="captcha-row">
            <img v-if="captchaImage" class="captcha-image" :src="captchaImage" alt="Distorted characters to type" />
            <span v-else class="captcha-image captcha-pending">Loading characters...</span>
            <button type="button" class="captcha-refresh" :disabled="captchaLoading" aria-label="Show different characters" title="Show different characters" @click="loadCaptcha">
              <RefreshCw :size="18" />
            </button>
          </div>
          <input
            id="captcha"
            v-model="captchaAnswer"
            type="text"
            autocomplete="off"
            autocapitalize="characters"
            spellcheck="false"
            maxlength="5"
            placeholder="Type the characters"
            required
          />
        </div>

        <p v-if="error || oauthError" class="error">{{ error || oauthError }}</p>
        <button
          v-if="unconfirmed"
          type="button"
          class="btn btn-oauth resend"
          :disabled="resending || !email"
          @click="handleResend"
        >
          {{ resending ? 'Sending...' : 'Resend confirmation email' }}
        </button>
        <p v-if="info" class="info">{{ info }}</p>

        <div class="signin-actions">
        <button type="submit" class="btn btn-primary" :disabled="loading || passkeyBusy || !captchaId">
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
        <PasskeyButton v-if="supported" icon-only :busy="passkeyBusy || loading" @click="handlePasskey(false)" />
        </div>
      </form>

      <p v-if="supported && passkeyMessage" class="passkey-message" role="status">{{ passkeyMessage }}</p>
      <p v-if="supported" class="footer-link"><a href="#email" @click.prevent="focusPasswordLogin">Lost access to your passkey? Sign in another way</a></p>

      <div class="divider">
        <span>or continue with</span>
      </div>

      <div class="oauth-buttons">
        <button class="btn btn-oauth" :disabled="loading" @click="handleGoogleLogin">
          Continue with Google
        </button>
      </div>

      <p class="footer-link">
        Don't have an account?
        <router-link to="/register">Register as an agent</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'
import { RefreshCw } from '@lucide/vue'
import PasskeyButton from '../components/PasskeyButton.vue'
import api from '../services/api.js'
import { usePasskeySupport } from '../composables/usePasskeySupport.js'
import { loginWithPasskey, primePasskeyLogin, cancelPasskeyCeremony, isCancelled, isAborted, FALLBACK_MESSAGE, passkeyErrorMessage } from '../services/passkeyService.js'
import { localCredentialIds } from '../utils/passkeyStorage.js'

const router = useRouter()
const { state, login, loginWithOAuth, handleOAuthCallback, resendVerificationEmail, getDashboardRoute, acceptPasskeySession } = useAuthStore()
const { supported, conditionalUI } = usePasskeySupport()
const passkeyBusy = ref(false), passkeyMessage = ref('')
let disposed = false, explicitStarted = false, primeTimer
function passkeyRequestHints() { return { email: email.value, credentialIds: localCredentialIds() } }
function schedulePasskeyChallenge() {
  clearTimeout(primeTimer)
  primeTimer = setTimeout(() => { primePasskeyLogin(passkeyRequestHints()).catch(() => {}) }, email.value ? 400 : 0)
}
function focusPasswordLogin() { document.getElementById('email')?.focus(); document.getElementById('email')?.scrollIntoView({ block: 'center', behavior: 'instant' }) }
async function handlePasskey(conditional) {
  if (!conditional && (passkeyBusy.value || loading.value)) return
  if (!conditional) { explicitStarted = true; passkeyBusy.value = true; passkeyMessage.value = '' }
  try {
    const data = await loginWithPasskey(conditional, conditional ? {} : passkeyRequestHints())
    if (disposed) return
    acceptPasskeySession(data)
    router.push(getDashboardRoute(data.role))
  } catch (err) {
    if (disposed || isAborted(err)) return
    if (conditional && explicitStarted) return
    passkeyMessage.value = isCancelled(err) || err.response?.data?.code === 'PASSKEY_FAILED'
      ? FALLBACK_MESSAGE : passkeyErrorMessage(err, 'Could not connect to sign in. Please try again.')
    if (!conditional) focusPasswordLogin()
  } finally { if (!conditional) passkeyBusy.value = false }
}
watch(() => [supported.value, conditionalUI.value], ([support, conditional]) => {
  const hash = window.location.hash
  const returningFromEmail = hash.includes('access_token') || hash.includes('error')
  if (support && conditional && !explicitStarted && !returningFromEmail && !new URLSearchParams(window.location.search).has('code')) handlePasskey(true)
})
onBeforeUnmount(() => { disposed = true; clearTimeout(primeTimer); cancelPasskeyCeremony() })

const email = ref('')
watch(email, schedulePasskeyChallenge)
const password = ref('')
const captchaId = ref('')
const captchaSvg = ref('')
const captchaAnswer = ref('')
const captchaLoading = ref(false)
const captchaImage = computed(() => captchaSvg.value ? `data:image/svg+xml;charset=utf-8,${encodeURIComponent(captchaSvg.value)}` : '')
const error = ref('')
const info = ref('')
const unconfirmed = ref(false)
const resending = ref(false)
const loading = ref(false)

const oauthError = computed(() => state.error)

function continueAfterSession(userData) {
  if (!userData) return
  if (userData.recovery) {
    router.replace('/reset-password')
    return
  }
  if (userData.needsProfile) {
    if (userData.suggestedFullName) {
      localStorage.setItem('suggested_full_name', userData.suggestedFullName)
    }
    router.push('/complete-profile')
    return
  }
  if (userData.role) {
    router.push(getDashboardRoute(userData.role))
  }
}

async function loadCaptcha() {
  captchaLoading.value = true
  captchaAnswer.value = ''
  try {
    const { data } = await api.get('/api/auth/captcha')
    captchaId.value = data.id
    captchaSvg.value = data.svg
  } catch {
    captchaId.value = ''
    captchaSvg.value = ''
    error.value = 'The human check could not be loaded. Try again.'
  } finally {
    captchaLoading.value = false
  }
}

async function handleLogin() {
  cancelPasskeyCeremony()
  error.value = ''
  info.value = ''
  unconfirmed.value = false
  loading.value = true

  try {
    const data = await login(email.value, password.value, { id: captchaId.value, answer: captchaAnswer.value })
    continueAfterSession(data)
  } catch (err) {
    unconfirmed.value = err.response?.data?.code === 'EMAIL_NOT_CONFIRMED'
    error.value = err.response?.data?.error || 'Invalid email or password'
    await loadCaptcha()
  } finally {
    loading.value = false
  }
}

async function handleResend() {
  info.value = ''
  error.value = ''
  resending.value = true
  try {
    const data = await resendVerificationEmail(email.value.trim().toLowerCase())
    info.value = data.message || 'Confirmation email sent.'
  } catch (err) {
    error.value = err.response?.data?.error || 'Could not resend the confirmation email.'
  } finally {
    resending.value = false
  }
}

async function handleGoogleLogin() {
  cancelPasskeyCeremony()
  error.value = ''
  loading.value = true
  try {
    await loginWithOAuth('google')
  } catch (err) {
    error.value = err.message || 'Google sign-in failed'
    loading.value = false
  }
}

onMounted(async () => {
  schedulePasskeyChallenge()
  loading.value = true
  const captchaPromise = loadCaptcha()
  try {
    continueAfterSession(await handleOAuthCallback())
  } finally {
    await captchaPromise
    loading.value = false
  }
})
</script>

<style scoped>
.auth-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
}

.auth-card {
  width: 100%;
  max-width: 420px;
  background: #fff;
  border-radius: 12px;
  padding: 2.5rem;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
}

h1 {
  font-size: 1.5rem;
  color: #16213e;
  margin-bottom: 0.25rem;
}

.subtitle {
  color: #6c757d;
  font-size: 0.875rem;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #334e68;
  margin-bottom: 0.375rem;
}

.password-label {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.75rem;
}

.password-label label {
  margin-bottom: 0.375rem;
}

.password-label a {
  color: #286848;
  font-size: 0.75rem;
  font-weight: 600;
  text-decoration: none;
}

.password-label a:hover {
  text-decoration: underline;
}

.info {
  color: #276749;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.resend {
  margin-bottom: 1rem;
}

.captcha-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.captcha-image {
  width: 210px;
  height: 68px;
  border: 1px solid #d5ded4;
  border-radius: 8px;
  background: #f3f7f1;
}

.captcha-pending {
  display: grid;
  place-items: center;
  color: #6c757d;
  font-size: 0.75rem;
}

.captcha-refresh {
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  border: 1px solid #d5ded4;
  border-radius: 8px;
  background: #fff;
  color: #176b55;
}

input {
  width: 100%;
  padding: 0.625rem 0.875rem;
  border: 1px solid #d9e2ec;
  border-radius: 8px;
  font-size: 0.9375rem;
  transition: border-color 0.2s;
}

input:focus {
  outline: none;
  border-color: #3e7cb1;
  box-shadow: 0 0 0 3px rgba(62, 124, 177, 0.15);
}

.error {
  color: #c81e1e;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.btn {
  min-height: 44px;
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 8px;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #3e7cb1;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #2f6a9b;
}

.divider {
  display: flex;
  align-items: center;
  margin: 1.5rem 0;
  color: #9fb3c8;
  font-size: 0.8125rem;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #d9e2ec;
}

.divider span {
  padding: 0 1rem;
}

.oauth-buttons {
  display: flex;
  gap: 0.75rem;
}

.btn-oauth {
  background: #fff;
  color: #334e68;
  border: 1px solid #d9e2ec;
}

.btn-oauth:hover:not(:disabled) {
  background: #f0f4f8;
}

.footer-link {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.875rem;
  color: #6c757d;
}

.footer-link a {
  color: #3e7cb1;
  text-decoration: none;
  font-weight: 500;
}

.footer-link a:hover {
  text-decoration: underline;
}
.passkey-message { margin-top:1rem; color:#52606d; font-size:.9rem; }
button:focus-visible, a:focus-visible { outline:3px solid #3e7cb1; outline-offset:3px; }
@media (max-width:480px) { .auth-page { padding:1rem; align-items:flex-start; } .auth-card { padding:1.25rem; } }
@media (prefers-reduced-motion:reduce) { * { transition:none !important; } }
</style>
