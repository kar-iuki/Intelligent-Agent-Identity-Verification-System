<template>
  <div class="auth-page">
    <div class="auth-card">
      <p class="auth-eyebrow">ACCOUNT RECOVERY</p>
      <h1>Choose a new password</h1>
      <p class="subtitle">Use at least 8 characters. You can sign in with it right away.</p>

      <form v-if="ready" @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="password">New password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            autocomplete="new-password"
            placeholder="Minimum 8 characters"
            required
          />
        </div>
        <div class="form-group">
          <label for="confirmPassword">Confirm password</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            autocomplete="new-password"
            placeholder="Re-enter your password"
            required
          />
        </div>

        <p v-if="error" class="error">{{ error }}</p>

        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? 'Updating...' : 'Update password' }}
        </button>
      </form>

      <template v-else>
        <p class="error">{{ error || 'Open the reset link from your email to choose a new password.' }}</p>
        <router-link to="/forgot-password" class="btn btn-primary">Request a new link</router-link>
      </template>

      <p class="footer-link">
        <router-link to="/login">Back to sign in</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'

const router = useRouter()
const { handleOAuthCallback, resetPassword, hasRecoverySession, getDashboardRoute } = useAuthStore()
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const ready = ref(false)
const loading = ref(false)

onMounted(async () => {
  const result = await handleOAuthCallback()
  if (result?.recovery || hasRecoverySession()) {
    ready.value = true
    return
  }
  if (result?.needsProfile) {
    router.replace('/complete-profile')
    return
  }
  if (result?.role) {
    router.replace(getDashboardRoute(result.role))
    return
  }
  ready.value = false
})

async function handleSubmit() {
  error.value = ''
  if (password.value.length < 8) {
    error.value = 'Password must be at least 8 characters'
    return
  }
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  loading.value = true
  try {
    const data = await resetPassword(password.value)
    if (data.passwordUpdated && !data.token) {
      router.push('/login')
      return
    }
    if (data.needsProfile) {
      router.push('/complete-profile')
      return
    }
    router.push(getDashboardRoute(data.role))
  } catch (err) {
    error.value = err.response?.data?.error || err.message || 'Could not update your password'
    if (err.response?.status === 401) ready.value = false
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page { display:flex; align-items:center; justify-content:center; min-height:100vh; padding:2rem; }
.auth-card { width:100%; max-width:420px; }
.form-group { margin-bottom:1.25rem; }
label { display:block; font-size:.875rem; font-weight:600; margin-bottom:.375rem; }
input { width:100%; padding:.625rem .875rem; border:1px solid #d5ded4; border-radius:8px; font-size:.9375rem; }
.error { color:#c81e1e; font-size:.875rem; margin-bottom:1rem; }
.btn { display:inline-block; min-height:44px; width:100%; padding:.75rem; border:none; border-radius:8px; font-weight:600; cursor:pointer; text-align:center; text-decoration:none; box-sizing:border-box; }
.btn-primary { background:#276b4f; color:#fff; }
.btn:disabled { opacity:.6; cursor:not-allowed; }
.footer-link { text-align:center; margin-top:1.5rem; font-size:.875rem; }
.footer-link a { color:#286848; font-weight:600; text-decoration:none; }
</style>
