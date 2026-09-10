<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1>Complete Your Profile</h1>
      <p class="subtitle">
        Google signed you in as <strong>{{ email }}</strong>. Add the details
        below to finish agent registration.
      </p>

      <form @submit.prevent="handleSubmit">
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
          <label for="phoneNumber">Phone Number</label>
          <input
            id="phoneNumber"
            v-model="form.phoneNumber"
            type="tel"
            placeholder="+1234567890"
            required
          />
          <span v-if="errors.phoneNumber" class="field-error">{{ errors.phoneNumber }}</span>
        </div>

        <div class="form-group">
          <label for="nationalID">National ID</label>
          <input
            id="nationalID"
            v-model="form.nationalID"
            type="text"
            placeholder="Your national ID number"
            required
          />
          <span v-if="errors.nationalID" class="field-error">{{ errors.nationalID }}</span>
        </div>

        <p v-if="errors.general" class="error">{{ errors.general }}</p>

        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? 'Saving...' : 'Save and Continue' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'

const router = useRouter()
const { state, completeProfile, fetchCurrentUser, getDashboardRoute } = useAuthStore()

const email = ref(state.user?.email || localStorage.getItem('oauth_email') || '')
const loading = ref(false)

const form = reactive({
  fullName: '',
  phoneNumber: '',
  nationalID: '',
})

const errors = reactive({
  fullName: '',
  phoneNumber: '',
  nationalID: '',
  general: '',
})

onMounted(async () => {
  try {
    const data = await fetchCurrentUser()
    if (data?.email) {
      email.value = data.email
      localStorage.setItem('oauth_email', data.email)
    }
    if (data && !data.needsProfile && data.role) {
      router.push(getDashboardRoute(data.role))
    }
  } catch {
    router.push('/login')
  }
})

function validate() {
  let valid = true
  Object.keys(errors).forEach((key) => { errors[key] = '' })

  if (!form.fullName.trim()) {
    errors.fullName = 'Full name is required'
    valid = false
  }
  if (!form.phoneNumber.trim()) {
    errors.phoneNumber = 'Phone number is required'
    valid = false
  }
  if (!form.nationalID.trim()) {
    errors.nationalID = 'National ID is required'
    valid = false
  }

  return valid
}

async function handleSubmit() {
  if (!validate()) return

  loading.value = true
  errors.general = ''

  try {
    await completeProfile(form)
    localStorage.removeItem('oauth_email')
    router.push('/pending')
  } catch (err) {
    errors.general = err.response?.data?.error || 'Failed to save profile'
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
  line-height: 1.5;
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
</style>
