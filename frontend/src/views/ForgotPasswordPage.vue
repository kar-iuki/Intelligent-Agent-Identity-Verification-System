<template>
  <div class="auth-page">
    <div class="auth-card">
      <p class="auth-eyebrow">ACCOUNT RECOVERY</p>
      <h1>Reset your password</h1>
      <p class="subtitle">Enter the email on your account. We will send a link to choose a new password.</p>

      <form v-if="!sent" @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            autocomplete="username"
            placeholder="you@example.com"
            required
          />
        </div>

        <p v-if="error" class="error">{{ error }}</p>

        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? 'Sending...' : 'Send reset link' }}
        </button>
      </form>

      <p v-else class="info">{{ message }}</p>

      <p class="footer-link">
        <router-link to="/login">Back to sign in</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/authStore.js'

const { forgotPassword } = useAuthStore()
const email = ref('')
const error = ref('')
const message = ref('')
const sent = ref(false)
const loading = ref(false)

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    const data = await forgotPassword(email.value)
    message.value = data.message || 'If an account exists for that email, a password reset link is on its way.'
    sent.value = true
  } catch (err) {
    error.value = err.response?.data?.error || 'Could not send the reset email.'
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
.info { color:#276749; font-size:.9375rem; line-height:1.6; }
.btn { min-height:44px; width:100%; padding:.75rem; border:none; border-radius:8px; font-weight:600; cursor:pointer; }
.btn-primary { background:#276b4f; color:#fff; }
.btn:disabled { opacity:.6; cursor:not-allowed; }
.footer-link { text-align:center; margin-top:1.5rem; font-size:.875rem; }
.footer-link a { color:#286848; font-weight:600; text-decoration:none; }
</style>
