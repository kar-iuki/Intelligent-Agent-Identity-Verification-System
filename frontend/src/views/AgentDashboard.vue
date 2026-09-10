<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <div>
        <h1>Agent Registration</h1>
        <p class="welcome">Welcome, {{ displayName }}</p>
      </div>
      <button class="btn-logout" @click="handleLogout">Sign Out</button>
    </header>

    <div class="dashboard-content">
      <div v-if="bootLoading" class="panel loading-panel">Loading your registration status...</div>

      <template v-else>
        <ol class="progress">
          <li :class="{ active: currentStep === 1, done: currentStep > 1 }">
            <span class="step-index">1</span>
            <span>Personal details</span>
          </li>
          <li :class="{ active: currentStep === 2, done: currentStep > 2 }">
            <span class="step-index">2</span>
            <span>Document upload</span>
          </li>
          <li :class="{ active: currentStep === 3, done: currentStep === 3 }">
            <span class="step-index">3</span>
            <span>Confirmation</span>
          </li>
        </ol>

        <!-- Step 1 -->
        <section v-if="currentStep === 1" class="panel">
          <h2>Personal details</h2>
          <p class="panel-copy">Confirm your identity details to continue registration.</p>

          <form class="form" @submit.prevent="handlePersonalDetails">
            <div class="form-group">
              <label for="email">Email</label>
              <input id="email" :value="email" type="email" readonly />
            </div>

            <div class="form-group">
              <label for="fullName">Full Name</label>
              <input
                id="fullName"
                v-model="personalForm.fullName"
                type="text"
                placeholder="Jane Mary Doe"
              />
              <span v-if="personalErrors.fullName" class="field-error">{{ personalErrors.fullName }}</span>
            </div>

            <div class="form-group">
              <label for="phoneNumber">Phone Number</label>
              <input
                id="phoneNumber"
                v-model="personalForm.phoneNumber"
                type="tel"
                placeholder="+254712345678"
              />
              <span v-if="personalErrors.phoneNumber" class="field-error">{{ personalErrors.phoneNumber }}</span>
            </div>

            <div class="form-group">
              <label for="nationalID">National ID Number</label>
              <input
                id="nationalID"
                v-model="personalForm.nationalID"
                type="text"
                placeholder="National ID number"
              />
              <span v-if="personalErrors.nationalID" class="field-error">{{ personalErrors.nationalID }}</span>
            </div>

            <p v-if="personalErrors.general" class="error">{{ personalErrors.general }}</p>

            <button type="submit" class="btn-primary" :disabled="savingDetails">
              {{ savingDetails ? 'Saving...' : 'Next' }}
            </button>
          </form>
        </section>

        <!-- Step 2 -->
        <section v-else-if="currentStep === 2" class="panel">
          <h2>Document upload</h2>
          <p class="panel-copy">
            Upload a clear government-issued ID and a live selfie. No verification runs in this step.
          </p>

          <div class="upload-grid">
            <ImageUpload
              v-model="documentFile"
              label="Identity document"
              accept="image/jpeg,image/png"
              :max-size="5"
              @file-selected="onDocumentSelected"
            />

            <div class="selfie-column">
              <ImageUpload
                v-model="selfieFile"
                label="Live selfie (upload)"
                accept="image/jpeg,image/png"
                :max-size="5"
                @file-selected="onSelfieSelected"
              />

              <CameraCapture
                label="Or capture with camera"
                @photo-captured="onCameraCaptured"
              />
            </div>
          </div>

          <p v-if="uploadError" class="error">{{ uploadError }}</p>

          <div class="actions-row">
            <button type="button" class="btn-secondary" @click="currentStep = 1">Back</button>
            <button
              type="button"
              class="btn-primary"
              :disabled="uploading"
              @click="handleDocumentUpload"
            >
              {{ uploading ? 'Uploading...' : 'Submit' }}
            </button>
          </div>
        </section>

        <!-- Step 3 -->
        <section v-else class="panel confirmation">
          <template v-if="verificationPhase === 'idle'">
            <div class="success-icon">✓</div>
            <h2>Documents submitted</h2>
            <p class="panel-copy">
              Your registration package has been received. Proceed when you are ready
              to start image quality checks.
            </p>

            <ul class="status-list">
              <li class="done">Personal Details Submitted</li>
              <li class="done">Documents Uploaded</li>
              <li class="pending">Verification Pending</li>
            </ul>

            <button
              type="button"
              class="btn-primary proceed-btn"
              @click="handleProceedToVerification"
            >
              Proceed to Verification
            </button>
          </template>

          <template v-else-if="verificationPhase === 'loading'">
            <div class="spinner" aria-hidden="true" />
            <h2>Checking image quality</h2>
            <p class="panel-copy">Checking image quality — please wait.</p>
          </template>

          <template v-else-if="verificationPhase === 'failed'">
            <div class="error-icon">!</div>
            <h2>Image quality check failed</h2>
            <p class="panel-copy">
              {{ qualityFailureSummary }}
              Please re-upload clearer images before verification can continue.
            </p>

            <ul class="failure-list">
              <li v-for="(item, index) in qualityFailures" :key="index">{{ item }}</li>
            </ul>

            <button type="button" class="btn-primary" @click="handleReupload">
              Re-upload Documents
            </button>
          </template>

          <template v-else-if="verificationPhase === 'passed'">
            <div class="success-icon">✓</div>
            <h2>Image quality checks passed</h2>
            <p class="panel-copy">
              Your images meet the quality requirements. Verification is continuing.
            </p>

            <ol class="pipeline-progress">
              <li class="complete">Image Quality ✓</li>
              <li class="pending-step">Document Verification — pending</li>
              <li class="pending-step">Face Matching — pending</li>
              <li class="pending-step">Liveness Detection — pending</li>
              <li class="pending-step">Verification Decision — pending</li>
            </ol>
          </template>

          <p v-if="verificationError" class="error">{{ verificationError }}</p>
        </section>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'
import ImageUpload from '../components/ImageUpload.vue'
import CameraCapture from '../components/CameraCapture.vue'
import {
  submitPersonalDetails,
  uploadDocuments,
  getProfile,
  getRegistrationStatus,
} from '../services/agentService.js'
import { initiateVerification } from '../services/verificationService.js'

const router = useRouter()
const { state, logout, fetchCurrentUser } = useAuthStore()

const bootLoading = ref(true)
const currentStep = ref(1)
const savingDetails = ref(false)
const uploading = ref(false)
const uploadError = ref('')
const documentFile = ref(null)
const selfieFile = ref(null)
const email = ref('')

// idle | loading | failed | passed
const verificationPhase = ref('idle')
const qualityFailures = ref([])
const failedImages = ref([])
const verificationError = ref('')

const personalForm = reactive({
  fullName: '',
  phoneNumber: '',
  nationalID: '',
})

const personalErrors = reactive({
  fullName: '',
  phoneNumber: '',
  nationalID: '',
  general: '',
})

const displayName = computed(() => {
  return personalForm.fullName || state.agent?.full_name || state.user?.email || 'Agent'
})

const qualityFailureSummary = computed(() => {
  const images = failedImages.value
  if (images.includes('document') && images.includes('selfie')) {
    return 'Both your document and selfie images failed quality checks.'
  }
  if (images.includes('document')) {
    return 'Your identity document image failed quality checks.'
  }
  if (images.includes('selfie')) {
    return 'Your selfie image failed quality checks.'
  }
  return 'One or more images failed quality checks.'
})

onMounted(async () => {
  try {
    await fetchCurrentUser()
    email.value = state.user?.email || ''

    const [{ status }, profile] = await Promise.all([
      getRegistrationStatus(),
      getProfile(),
    ])

    email.value = profile.email || email.value

    if (profile.agent) {
      personalForm.fullName = profile.agent.full_name || ''
      personalForm.phoneNumber = profile.agent.phone_number || ''
      personalForm.nationalID = profile.agent.national_id || ''
    }

    if (!personalForm.fullName) {
      personalForm.fullName = state.agent?.full_name || ''
    }

    currentStep.value = mapStatusToStep(status)
  } catch (err) {
    personalErrors.general = err.response?.data?.error || 'Failed to load registration status'
  } finally {
    bootLoading.value = false
  }
})

function mapStatusToStep(status) {
  if (status === 'verification_pending') return 3
  if (status === 'documents_submitted') return 2
  return 1
}

function validatePersonalDetails() {
  let valid = true
  personalErrors.fullName = ''
  personalErrors.phoneNumber = ''
  personalErrors.nationalID = ''
  personalErrors.general = ''

  const name = personalForm.fullName.trim()
  const words = name.split(/\s+/).filter(Boolean)

  if (words.length < 2) {
    personalErrors.fullName = 'Enter your full name (at least two words)'
    valid = false
  }

  const phone = personalForm.phoneNumber.trim()
  if (!/^\+?[0-9\s()-]{7,20}$/.test(phone)) {
    personalErrors.phoneNumber = 'Enter a valid phone number'
    valid = false
  }

  if (!personalForm.nationalID.trim()) {
    personalErrors.nationalID = 'National ID is required'
    valid = false
  }

  return valid
}

async function handlePersonalDetails() {
  if (!validatePersonalDetails()) return

  savingDetails.value = true
  personalErrors.general = ''

  try {
    await submitPersonalDetails({
      fullName: personalForm.fullName.trim(),
      phoneNumber: personalForm.phoneNumber.trim(),
      nationalID: personalForm.nationalID.trim(),
    })
    currentStep.value = 2
  } catch (err) {
    personalErrors.general =
      err.response?.data?.error || 'Failed to save personal details'
  } finally {
    savingDetails.value = false
  }
}

function onDocumentSelected(file) {
  documentFile.value = file
  uploadError.value = ''
}

function onSelfieSelected(file) {
  selfieFile.value = file
  uploadError.value = ''
}

function onCameraCaptured(file) {
  selfieFile.value = file
  uploadError.value = ''
}

function validateFiles() {
  uploadError.value = ''

  if (!documentFile.value || !selfieFile.value) {
    uploadError.value = 'Both an identity document and a selfie are required'
    return false
  }

  const allowed = ['image/jpeg', 'image/png']
  const maxBytes = 5 * 1024 * 1024

  for (const file of [documentFile.value, selfieFile.value]) {
    if (!allowed.includes(file.type)) {
      uploadError.value = 'Only JPEG and PNG images are allowed'
      return false
    }
    if (file.size > maxBytes) {
      uploadError.value = 'Each file must be 5MB or smaller'
      return false
    }
  }

  return true
}

async function handleDocumentUpload() {
  if (!validateFiles()) return

  uploading.value = true
  uploadError.value = ''

  try {
    await uploadDocuments(documentFile.value, selfieFile.value)
    verificationPhase.value = 'idle'
    qualityFailures.value = []
    failedImages.value = []
    verificationError.value = ''
    currentStep.value = 3
  } catch (err) {
    uploadError.value = err.response?.data?.error || 'Document upload failed'
  } finally {
    uploading.value = false
  }
}

async function handleProceedToVerification() {
  verificationPhase.value = 'loading'
  verificationError.value = ''
  qualityFailures.value = []
  failedImages.value = []

  try {
    const result = await initiateVerification()

    if (!result.overallPassed) {
      verificationPhase.value = 'failed'
      qualityFailures.value = result.failures || []
      failedImages.value = result.failedImages || []
      return
    }

    verificationPhase.value = 'passed'
  } catch (err) {
    verificationPhase.value = 'idle'
    verificationError.value =
      err.response?.data?.error || err.message || 'Verification request failed'
  }
}

function handleReupload() {
  verificationPhase.value = 'idle'
  qualityFailures.value = []
  failedImages.value = []
  verificationError.value = ''
  documentFile.value = null
  selfieFile.value = null
  currentStep.value = 2
}

async function handleLogout() {
  await logout()
  router.push('/login')
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: linear-gradient(180deg, #eef3f8 0%, #f8fafc 40%, #f8fafc 100%);
}

.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 2rem;
  background: rgba(255, 255, 255, 0.9);
  border-bottom: 1px solid #d9e2ec;
}

h1 {
  font-size: 1.25rem;
  color: #16213e;
}

.welcome {
  color: #627d98;
  font-size: 0.875rem;
  margin-top: 0.15rem;
}

.btn-logout {
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid #d9e2ec;
  border-radius: 8px;
  color: #52606d;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-logout:hover {
  background: #f0f4f8;
}

.dashboard-content {
  padding: 2rem;
  max-width: 920px;
  margin: 0 auto;
}

.progress {
  list-style: none;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.progress li {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.85rem 1rem;
  border-radius: 10px;
  background: #fff;
  color: #829ab1;
  border: 1px solid #e2e8f0;
  font-size: 0.875rem;
  font-weight: 500;
}

.progress li.active {
  color: #243b53;
  border-color: #3e7cb1;
  box-shadow: 0 0 0 3px rgba(62, 124, 177, 0.12);
}

.progress li.done {
  color: #276749;
  border-color: #9ae6b4;
}

.step-index {
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #edf2f7;
  font-size: 0.75rem;
  font-weight: 700;
}

.progress li.active .step-index {
  background: #3e7cb1;
  color: #fff;
}

.progress li.done .step-index {
  background: #38a169;
  color: #fff;
}

.panel {
  background: #fff;
  border-radius: 14px;
  padding: 2rem;
  box-shadow: 0 2px 14px rgba(15, 23, 42, 0.06);
}

.loading-panel {
  text-align: center;
  color: #627d98;
}

h2 {
  font-size: 1.35rem;
  color: #16213e;
  margin-bottom: 0.35rem;
}

.panel-copy {
  color: #627d98;
  margin-bottom: 1.5rem;
  line-height: 1.55;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 480px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #334e68;
}

input {
  padding: 0.7rem 0.85rem;
  border: 1px solid #d9e2ec;
  border-radius: 8px;
  font-size: 0.95rem;
}

input:focus {
  outline: none;
  border-color: #3e7cb1;
  box-shadow: 0 0 0 3px rgba(62, 124, 177, 0.15);
}

input[readonly] {
  background: #f5f7fa;
  color: #486581;
}

.field-error,
.error {
  color: #c81e1e;
  font-size: 0.8125rem;
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.25rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
}

.btn-primary {
  background: #3e7cb1;
  color: #fff;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary:hover:not(:disabled) {
  background: #2f6a9b;
}

.btn-secondary {
  background: #fff;
  color: #334e68;
  border: 1px solid #d9e2ec;
}

.upload-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1.25rem;
}

.selfie-column {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.actions-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.confirmation {
  text-align: center;
  max-width: 560px;
  margin: 0 auto;
}

.success-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto 1rem;
  border-radius: 50%;
  background: #d4edda;
  color: #155724;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
}

.status-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1.5rem;
  text-align: left;
}

.status-list li {
  padding: 0.85rem 1rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
}

.status-list li.done {
  background: #f0fff4;
  color: #276749;
}

.status-list li.pending {
  background: #fffbeb;
  color: #975a16;
}

.proceed-btn {
  margin-top: 1.5rem;
}

.spinner {
  width: 48px;
  height: 48px;
  margin: 0 auto 1.25rem;
  border: 4px solid #d9e2ec;
  border-top-color: #3e7cb1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto 1rem;
  border-radius: 50%;
  background: #fed7d7;
  color: #9b2c2c;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
}

.failure-list {
  list-style: none;
  text-align: left;
  margin: 0 auto 1.5rem;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.failure-list li {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  background: #fff5f5;
  color: #9b2c2c;
  font-size: 0.9rem;
  font-weight: 500;
}

.pipeline-progress {
  list-style: none;
  text-align: left;
  margin: 1.5rem auto 0;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.pipeline-progress li {
  padding: 0.8rem 1rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
}

.pipeline-progress li.complete {
  background: #f0fff4;
  color: #276749;
}

.pipeline-progress li.pending-step {
  background: #f7fafc;
  color: #718096;
}

@media (max-width: 768px) {
  .dashboard-content {
    padding: 1rem;
  }

  .progress {
    grid-template-columns: 1fr;
  }

  .upload-grid {
    grid-template-columns: 1fr;
  }
}
</style>
