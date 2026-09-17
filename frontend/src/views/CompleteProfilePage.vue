<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1>Complete Your Profile</h1>
      <p class="subtitle">
        Signed in as <strong>{{ email }}</strong>. Add your phone number, national ID,
        and date of birth to finish registration.
      </p>

      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="fullName">Full Name</label>
          <input
            id="fullName"
            v-model="form.fullName"
            type="text"
            placeholder="John Doe"
            :readonly="nameLocked"
            :class="{ readonly: nameLocked }"
            required
          />
          <span v-if="nameLocked" class="hint">Taken from your account / Google profile</span>
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

        <div class="form-group">
          <label for="dateOfBirth">Date of Birth</label>
          <input
            id="dateOfBirth"
            v-model="form.dateOfBirth"
            type="date"
            :max="maxDateOfBirth"
            required
          />
          <span class="hint">Must match the date on your ID or passport</span>
          <span v-if="errors.dateOfBirth" class="field-error">{{ errors.dateOfBirth }}</span>
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
import { reactive, ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'

const router = useRouter()
const { state, completeProfile, fetchCurrentUser, getDashboardRoute } = useAuthStore()

const email = ref(state.user?.email || localStorage.getItem('oauth_email') || '')
const loading = ref(false)
const suggestedName = ref(localStorage.getItem('suggested_full_name') || '')

const form = reactive({
  fullName: '',
  phoneNumber: '',
  nationalID: '',
  dateOfBirth: '',
})

const errors = reactive({
  fullName: '',
  phoneNumber: '',
  nationalID: '',
  dateOfBirth: '',
  general: '',
})

const maxDateOfBirth = computed(() => {
  const d = new Date()
  d.setFullYear(d.getFullYear() - 18)
  return d.toISOString().slice(0, 10)
})

const nameLocked = computed(() => Boolean(suggestedName.value?.trim()))

onMounted(async () => {
  try {
    const data = await fetchCurrentUser()
    if (data?.email) {
      email.value = data.email
      localStorage.setItem('oauth_email', data.email)
    }
    if (data?.suggestedFullName) {
      suggestedName.value = data.suggestedFullName
      localStorage.setItem('suggested_full_name', data.suggestedFullName)
    }
    if (suggestedName.value) {
      form.fullName = suggestedName.value
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

  if (!form.dateOfBirth) {
    errors.dateOfBirth = 'Date of birth is required'
    valid = false
  } else {
    const date = new Date(`${form.dateOfBirth}T00:00:00`)
    if (Number.isNaN(date.getTime())) {
      errors.dateOfBirth = 'Enter a valid date of birth'
      valid = false
    } else {
      const now = new Date()
      const ageYears = (now - date) / (365.25 * 24 * 60 * 60 * 1000)
      if (ageYears < 18) {
        errors.dateOfBirth = 'You must be at least 18 years old'
        valid = false
      }
    }
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
    localStorage.removeItem('suggested_full_name')
    sessionStorage.removeItem('pending_verify_email')
    router.push('/agent/dashboard')
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

input.readonly {
  background: #f7fafc;
  color: #243b53;
}

input:focus {
  outline: none;
  border-color: #3e7cb1;
  box-shadow: 0 0 0 3px rgba(62, 124, 177, 0.15);
}

.hint {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #829ab1;
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
