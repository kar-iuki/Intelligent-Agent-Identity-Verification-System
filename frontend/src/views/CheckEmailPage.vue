<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="icon">✉</div>
      <h1>Check your email</h1>
      <p>
        We sent a confirmation link to
        <strong>{{ email || 'your email' }}</strong>.
      </p>
      <p class="note">
        Open the email and click the link to verify your account. After that you will
        finish your profile with phone number and national ID.
      </p>

      <p v-if="info" class="info">{{ info }}</p>
      <p v-if="error" class="error">{{ error }}</p>

      <button
        type="button"
        class="btn btn-secondary"
        :disabled="resending || cooldown > 0 || !email"
        @click="handleResend"
      >
        {{
          cooldown > 0
            ? `Resend email in ${cooldown}s`
            : resending
              ? 'Sending...'
              : 'Resend confirmation email'
        }}
      </button>

      <router-link to="/login" class="btn btn-primary">Go to Sign In</router-link>

      <p class="footer-link">
        Wrong email?
        <router-link to="/register">Register again</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'

const route = useRoute()
const { resendVerificationEmail } = useAuthStore()

const info = ref('')
const error = ref('')
const resending = ref(false)
const cooldown = ref(0)
let cooldownTimer = null

const email = computed(() => {
  const fromQuery = typeof route.query.email === 'string' ? route.query.email : ''
  return (fromQuery || sessionStorage.getItem('pending_verify_email') || '').trim().toLowerCase()
})

function startCooldown(seconds = 60) {
  cooldown.value = seconds
  if (cooldownTimer) clearInterval(cooldownTimer)
  cooldownTimer = setInterval(() => {
    cooldown.value -= 1
    if (cooldown.value <= 0) {
      clearInterval(cooldownTimer)
      cooldownTimer = null
    }
  }, 1000)
}

onBeforeUnmount(() => {
  if (cooldownTimer) clearInterval(cooldownTimer)
})

async function handleResend() {
  info.value = ''
  error.value = ''
  if (!email.value) {
    error.value = 'Missing email address. Please register again.'
    return
  }

  resending.value = true
  try {
    const data = await resendVerificationEmail(email.value)
    info.value = data.message || 'Confirmation email resent.'
    startCooldown(60)
  } catch (err) {
    error.value = err.response?.data?.error || 'Could not resend the email.'
  } finally {
    resending.value = false
  }
}
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
  max-width: 480px;
  background: #fff;
  border-radius: 12px;
  padding: 2.5rem;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.icon {
  width: 56px;
  height: 56px;
  margin: 0 auto 1.5rem;
  background: #dbeafe;
  color: #1d4ed8;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
}

h1 {
  font-size: 1.5rem;
  color: #16213e;
  margin-bottom: 1rem;
}

p {
  color: #52606d;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.note {
  font-size: 0.875rem;
  color: #829ab1;
}

.info {
  color: #276749;
  font-size: 0.875rem;
}

.error {
  color: #c81e1e;
  font-size: 0.875rem;
}

.btn {
  display: inline-block;
  width: 100%;
  margin-top: 0.75rem;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  box-sizing: border-box;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #3e7cb1;
  color: #fff;
}

.btn-secondary {
  background: #edf2f7;
  color: #2d3748;
}

.footer-link {
  margin-top: 1.5rem;
  font-size: 0.875rem;
  color: #6c757d;
}

.footer-link a {
  color: #3e7cb1;
  text-decoration: none;
  font-weight: 500;
}
</style>
