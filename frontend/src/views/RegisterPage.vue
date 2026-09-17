<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1>Agent Registration</h1>
      <p class="subtitle">Create your account. We will email you a confirmation link.</p>

      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="fullName">Full Name</label>
          <input
            id="fullName"
            v-model="form.fullName"
            type="text"
            placeholder="John Doe"
            required
          />
          <span v-if="errors.fullName" class="field-error">{{ errors.fullName }}</span>
        </div>

        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="you@example.com"
            required
          />
          <span v-if="errors.email" class="field-error">{{ errors.email }}</span>
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="Minimum 8 characters"
            required
          />
          <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
        </div>

        <div class="form-group">
          <label for="confirmPassword">Confirm password</label>
          <input
            id="confirmPassword"
            v-model="form.confirmPassword"
            type="password"
            placeholder="Re-enter your password"
            required
          />
          <span v-if="errors.confirmPassword" class="field-error">{{ errors.confirmPassword }}</span>
        </div>

        <p v-if="errors.general" class="error">{{ errors.general }}</p>

        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? 'Registering...' : 'Register' }}
        </button>
      </form>

      <p class="footer-link">
        Already have an account?
        <router-link to="/login">Sign in</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'
import { messageFromGuardrailError } from '../utils/deviceFingerprint.js'

const router = useRouter()
const { register } = useAuthStore()

const form = reactive({
  fullName: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const errors = reactive({
  fullName: '',
  email: '',
  password: '',
  confirmPassword: '',
  general: '',
})

const loading = ref(false)

function validate() {
  let valid = true
  Object.keys(errors).forEach((key) => { errors[key] = '' })

  if (!form.fullName.trim()) {
    errors.fullName = 'Full name is required'
    valid = false
  }

  if (!form.email.trim()) {
    errors.email = 'Email is required'
    valid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = 'Enter a valid email address'
    valid = false
  }

  if (!form.password) {
    errors.password = 'Password is required'
    valid = false
  } else if (form.password.length < 8) {
    errors.password = 'Password must be at least 8 characters'
    valid = false
  }

  if (!form.confirmPassword) {
    errors.confirmPassword = 'Please re-enter your password'
    valid = false
  } else if (form.confirmPassword !== form.password) {
    errors.confirmPassword = 'Passwords do not match'
    valid = false
  }

  return valid
}

async function handleRegister() {
  if (!validate()) return

  loading.value = true
  errors.general = ''

  try {
    const data = await register(form)
    const email = data.email || form.email.trim().toLowerCase()
    sessionStorage.setItem('pending_verify_email', email)

    if (data.requiresEmailVerification) {
      router.push({ name: 'check-email', query: { email } })
      return
    }

    if (data.needsProfile) {
      router.push('/complete-profile')
      return
    }

    router.push('/login')
  } catch (err) {
    errors.general = messageFromGuardrailError(err)
  } finally {
    loading.value = false
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
  max-width: 460px;
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

.field-error {
  display: block;
  color: #c81e1e;
  font-size: 0.8125rem;
  margin-top: 0.25rem;
}

.error {
  color: #c81e1e;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.btn {
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
</style>
