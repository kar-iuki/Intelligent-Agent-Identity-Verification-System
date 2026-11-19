<template>
  <div class="auth-page">
    <div class="auth-card">
      <span class="entry-symbol" aria-hidden="true"><Mail :size="24" /></span>
      <h1>Check your email</h1>
      <p>
        We sent a confirmation link to
        <strong>{{ email || 'your email' }}</strong>.
      </p>
      <p class="note">
        Open the link, then finish your profile with your phone number and national ID.
      </p>

      <p v-if="info" role="status" class="info">{{ info }}</p>
      <p v-if="error" role="alert" class="error">{{ error }}</p>

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

      <router-link to="/login" class="btn btn-primary">Go to sign in</router-link>

      <p class="footer-link">
        Wrong email?
        <router-link to="/register">Register again</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { Mail } from '@lucide/vue'
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
h1 {
  font-size: 1.5rem;
  color: var(--ink);
  margin-bottom: 1rem;
}

p {
  color: var(--ink);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.note {
  font-size: 0.875rem;
  color: var(--muted);
}

.info {
  color: var(--success);
  font-size: 0.875rem;
}

.error {
  color: var(--danger);
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
  background: var(--action);
  color: var(--on-brand);
}

.btn-secondary {
  background: var(--surface-muted);
  color: var(--ink);
}

.footer-link {
  margin-top: 1.5rem;
  font-size: 0.875rem;
  color: var(--muted);
}

.footer-link a {
  color: var(--link);
  text-decoration: none;
  font-weight: 500;
}
</style>
