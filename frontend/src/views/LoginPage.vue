<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1>Sign In</h1>
      <p class="subtitle">Intelligent Agent Identity Verification System</p>

      <template v-if="supported && promotePasskey">
        <PasskeyButton prominent :busy="passkeyBusy || loading" @click="handlePasskey(false)" />
        <div class="divider"><span>or</span></div>
      </template>
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
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            autocomplete="current-password"
            placeholder="Enter your password"
            required
          />
        </div>

        <p v-if="error || oauthError" class="error">{{ error || oauthError }}</p>

        <button type="submit" class="btn btn-primary" :disabled="loading || passkeyBusy">
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>

      <template v-if="supported && !promotePasskey">
        <div class="divider"><span>or</span></div>
        <PasskeyButton :busy="passkeyBusy || loading" @click="handlePasskey(false)" />
      </template>
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
import PasskeyButton from '../components/PasskeyButton.vue'
import { usePasskeySupport } from '../composables/usePasskeySupport.js'
import { readLocal } from '../utils/passkeyStorage.js'
import { loginWithPasskey, cancelPasskeyCeremony, isCancelled, isAborted, FALLBACK_MESSAGE } from '../services/passkeyService.js'

const router = useRouter()
const { state, login, loginWithOAuth, handleOAuthCallback, getDashboardRoute, acceptPasskeySession } = useAuthStore()
const { supported, conditionalUI } = usePasskeySupport()
const promotePasskey = ref(readLocal('passkey_registered_any') === true)
const passkeyBusy = ref(false), passkeyMessage = ref('')
let disposed = false, explicitStarted = false
function focusPasswordLogin() { document.getElementById('email')?.focus(); document.getElementById('email')?.scrollIntoView({ block: 'center', behavior: 'instant' }) }
function refreshPromotion() { promotePasskey.value = readLocal('passkey_registered_any') === true }
async function handlePasskey(conditional) {
  if (!conditional && (passkeyBusy.value || loading.value)) return
  if (!conditional) { explicitStarted = true; passkeyBusy.value = true; passkeyMessage.value = '' }
  try {
    const data = await loginWithPasskey(conditional)
    if (disposed) return
    acceptPasskeySession(data)
    router.push(getDashboardRoute(data.role))
  } catch (err) {
    if (disposed || isAborted(err)) return
    if (conditional && explicitStarted) return
    passkeyMessage.value = isCancelled(err) || err.response?.data?.code === 'PASSKEY_FAILED'
      ? FALLBACK_MESSAGE : 'Could not connect to sign in. Please try again.'
    if (!conditional) focusPasswordLogin()
  } finally { if (!conditional) passkeyBusy.value = false }
}
watch(() => [supported.value, conditionalUI.value], ([support, conditional]) => {
  if (support && conditional && !explicitStarted && !new URLSearchParams(window.location.search).has('code')) handlePasskey(true)
})
onMounted(() => window.addEventListener('storage', refreshPromotion))
onBeforeUnmount(() => { disposed = true; cancelPasskeyCeremony(); window.removeEventListener('storage', refreshPromotion) })

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const oauthError = computed(() => state.error)

async function handleLogin() {
  cancelPasskeyCeremony()
  error.value = ''
  loading.value = true

  try {
    const data = await login(email.value, password.value)
    if (data.needsProfile) {
      router.push('/complete-profile')
      return
    }
    router.push(getDashboardRoute(data.role))
  } catch (err) {
    error.value = err.response?.data?.error || 'Invalid email or password'
  } finally {
    loading.value = false
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
  loading.value = true
  try {
    const userData = await handleOAuthCallback()
    if (!userData) return

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
  } finally {
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
