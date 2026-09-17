<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <div>
        <h1>Agent Registration</h1>
        <p class="welcome">Welcome, {{ displayName }}</p>
      </div>
      <div class="header-actions">
        <router-link class="btn-link" to="/agent/audit">My audit trail</router-link>
        <button class="btn-logout" @click="handleLogout">Sign Out</button>
      </div>
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
            <span>Identity document</span>
          </li>
          <li :class="{ active: currentStep === 3, done: currentStep > 3 }">
            <span class="step-index">3</span>
            <span>Live selfie</span>
          </li>
          <li :class="{ active: currentStep === 4, done: currentStep === 4 }">
            <span class="step-index">4</span>
            <span>Verification</span>
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

            <div class="form-group">
              <label for="dateOfBirth">Date of Birth</label>
              <input
                id="dateOfBirth"
                v-model="personalForm.dateOfBirth"
                type="date"
                :max="maxDateOfBirth"
              />
              <span class="field-hint">Must match the date on your ID or passport</span>
              <span v-if="personalErrors.dateOfBirth" class="field-error">{{ personalErrors.dateOfBirth }}</span>
            </div>

            <p v-if="personalErrors.general" class="error">{{ personalErrors.general }}</p>

            <button type="submit" class="btn-primary" :disabled="savingDetails">
              {{ savingDetails ? 'Saving...' : 'Next' }}
            </button>
          </form>
        </section>

        <!-- Step 2: document type + quality-gated capture -->
        <section v-else-if="currentStep === 2" class="panel">
          <h2>Identity document</h2>
          <p v-if="recaptureMode === 'document'" class="panel-copy recapture-note">
            Your selfie is fine — only recapture the identity document that failed quality checks.
          </p>
          <p v-else class="panel-copy">
            Choose your document type. Each photo is quality-checked before you can continue —
            this helps OCR read your details correctly.
          </p>

          <div v-if="docSubstep === 'choose'" class="doc-type-grid">
            <button type="button" class="doc-type-card" @click="selectDocKind('national_id')">
              <strong>National ID</strong>
              <span>Capture front, then back</span>
            </button>
            <button type="button" class="doc-type-card" @click="selectDocKind('passport')">
              <strong>Passport</strong>
              <span>Bio-data page only</span>
            </button>
            <button type="button" class="btn-secondary" @click="currentStep = 1">Back</button>
          </div>

          <DocumentCaptureStep
            v-else-if="docSubstep === 'front'"
            :title="documentKind === 'passport' ? 'Passport bio-data page' : 'ID front'"
            :hint="documentKind === 'passport'
              ? 'Capture the page with your photo and personal details.'
              : 'Capture the front of your national ID. Keep text sharp and evenly lit.'"
            :initial-file="documentFrontFile"
            @back="onDocumentFrontBack"
            @passed="onFrontPassed"
          />

          <DocumentCaptureStep
            v-else-if="docSubstep === 'back'"
            title="ID back"
            hint="Capture the back of your national ID."
            :initial-file="documentBackFile"
            @back="docSubstep = 'front'"
            @passed="onBackPassed"
          />
          <p v-if="uploadError" class="error">{{ uploadError }}</p>
          <p v-if="uploading" class="panel-copy">Uploading documents…</p>
        </section>

        <!-- Step 3: live selfie challenge -->
        <section v-else-if="currentStep === 3" class="panel">
          <p v-if="recaptureMode === 'selfie'" class="panel-copy recapture-note">
            Your identity document is fine — only retake the live selfie.
          </p>
          <LiveSelfieChallenge
            @back="backFromSelfie"
            @passed="onSelfiePassed"
          />
          <p v-if="uploadError" class="error">{{ uploadError }}</p>
          <p v-if="uploading" class="panel-copy">Uploading documents…</p>
        </section>

        <!-- Step 4: verification -->
        <section v-else class="panel confirmation">
          <template v-if="verificationPhase === 'idle'">
            <div class="success-icon">✓</div>
            <h2>Documents submitted</h2>
            <p class="panel-copy">
              Your identity document and live selfie passed capture checks.
              Proceed when you are ready to run full verification.
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
            <h2>Running verification checks</h2>
            <p class="panel-copy">Running image quality, OCR, face matching, and liveness checks — please wait.</p>
          </template>

          <template v-else-if="verificationPhase === 'failed'">
            <div class="error-icon">!</div>
            <h2>Image quality check failed</h2>
            <p class="panel-copy">
              {{ qualityFailureSummary }}
              Only the failed image(s) need to be recaptured.
            </p>

            <ul class="failure-list">
              <li v-for="(item, index) in qualityFailures" :key="index">{{ item }}</li>
            </ul>

            <button type="button" class="btn-primary" @click="handleReupload">
              {{ recaptureButtonLabel }}
            </button>
          </template>

          <template v-else-if="verificationPhase === 'passed' || verificationPhase === 'decision'">
            <ol class="pipeline-progress">
              <li
                v-for="step in pipelineSteps"
                :key="step.label"
                :class="step.complete ? 'complete' : 'pending-step'"
              >
                {{ step.label }}
              </li>
            </ol>

            <template v-if="finalDecision === 'verified'">
              <div class="banner banner-success">Your identity has been verified</div>
              <p class="panel-copy">
                You now have full platform access. Continue to the agent workspace to get started.
              </p>
              <button type="button" class="btn-primary" @click="router.push('/agent/platform')">
                Proceed to Platform
              </button>
            </template>

            <template v-else-if="finalDecision === 'review'">
              <div class="banner banner-review">Your verification is under review</div>
              <p class="panel-copy">
                An administrator is reviewing your case. You will be notified once a decision is made.
                No further action is required from you right now.
              </p>
            </template>

            <template v-else-if="finalDecision === 'rejected'">
              <div class="banner banner-rejected">Your verification was unsuccessful</div>
              <p class="panel-copy">
                Your identity could not be verified with the documents provided.
                If you believe this is an error, please contact support.
              </p>
              <a class="support-link" href="mailto:support@example.com">Contact support</a>
            </template>

            <template v-else>
              <div class="spinner" aria-hidden="true" />
              <h2>Finalising decision</h2>
              <p class="panel-copy">Waiting for the access control decision...</p>
            </template>
          </template>

          <p v-if="verificationError" class="error">{{ verificationError }}</p>
        </section>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'
import DocumentCaptureStep from '../components/DocumentCaptureStep.vue'
import LiveSelfieChallenge from '../components/LiveSelfieChallenge.vue'
import {
  submitPersonalDetails,
  uploadDocuments,
  getProfile,
  getRegistrationStatus,
} from '../services/agentService.js'
import {
  initiateVerification,
  getVerificationStatus,
} from '../services/verificationService.js'
import {
  getDeviceFingerprint,
  messageFromGuardrailError,
} from '../utils/deviceFingerprint.js'

const router = useRouter()
const { state, logout, fetchCurrentUser } = useAuthStore()

const bootLoading = ref(true)
const currentStep = ref(1)
const savingDetails = ref(false)
const uploading = ref(false)
const uploadError = ref('')
const email = ref('')

const documentKind = ref('national_id') // national_id | passport
const docSubstep = ref('choose') // choose | front | back
const documentFrontFile = ref(null)
const documentBackFile = ref(null)
const selfieFile = ref(null)
const selfieChallenge = ref(null)
/** null | 'selfie' | 'document' | 'both' — targeted recapture after verification quality failure */
const recaptureMode = ref(null)
// idle | loading | failed | passed | decision
const verificationPhase = ref('idle')
const qualityFailures = ref([])
const failedImages = ref([])
const verificationError = ref('')
const finalDecision = ref(null)
const pipelineState = ref({
  imageQuality: 'pending',
  documentVerification: 'pending',
  faceMatching: 'pending',
  livenessDetection: 'pending',
  verificationDecision: 'pending',
})

let pollTimer = null

const pipelineSteps = computed(() => [
  {
    label: pipelineState.value.imageQuality === 'complete' ? 'Image Quality ✓' : 'Image Quality — pending',
    complete: pipelineState.value.imageQuality === 'complete',
  },
  {
    label: pipelineState.value.documentVerification === 'complete' ? 'Document Verification ✓' : 'Document Verification — pending',
    complete: pipelineState.value.documentVerification === 'complete',
  },
  {
    label: pipelineState.value.faceMatching === 'complete' ? 'Face Matching ✓' : 'Face Matching — pending',
    complete: pipelineState.value.faceMatching === 'complete',
  },
  {
    label: pipelineState.value.livenessDetection === 'complete' ? 'Liveness Detection ✓' : 'Liveness Detection — pending',
    complete: pipelineState.value.livenessDetection === 'complete',
  },
  {
    label: pipelineState.value.verificationDecision === 'complete' ? 'Verification Decision ✓' : 'Verification Decision — pending',
    complete: pipelineState.value.verificationDecision === 'complete',
  },
])

const personalForm = reactive({
  fullName: '',
  phoneNumber: '',
  nationalID: '',
  dateOfBirth: '',
})

const personalErrors = reactive({
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

const recaptureButtonLabel = computed(() => {
  const images = failedImages.value
  const needsDocument = images.includes('document')
  const needsSelfie = images.includes('selfie')
  if (needsSelfie && !needsDocument) return 'Recapture selfie'
  if (needsDocument && !needsSelfie) return 'Recapture identity document'
  return 'Recapture failed images'
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
      personalForm.dateOfBirth = profile.agent.date_of_birth?.slice?.(0, 10) || profile.agent.date_of_birth || ''
    }

    if (!personalForm.fullName) {
      personalForm.fullName = state.agent?.full_name || ''
    }

    currentStep.value = mapStatusToStep(status)

    if (currentStep.value === 4) {
      await refreshVerificationStatus()
      startPollingIfNeeded()
    }
  } catch (err) {
    personalErrors.general = err.response?.data?.error || 'Failed to load registration status'
  } finally {
    bootLoading.value = false
  }
})

onBeforeUnmount(() => {
  stopPolling()
})

function mapStatusToStep(status) {
  if (status === 'verification_pending') return 4
  if (status === 'documents_submitted') return 2
  return 1
}

function selectDocKind(kind) {
  documentKind.value = kind
  documentFrontFile.value = null
  documentBackFile.value = null
  docSubstep.value = 'front'
  uploadError.value = ''
}

function onDocumentFrontBack() {
  if (recaptureMode.value === 'document' || recaptureMode.value === 'both') {
    currentStep.value = 4
    verificationPhase.value = 'failed'
    return
  }
  docSubstep.value = 'choose'
}

function returnToVerificationReady() {
  recaptureMode.value = null
  verificationPhase.value = 'idle'
  qualityFailures.value = []
  failedImages.value = []
  verificationError.value = ''
  uploadError.value = ''
  currentStep.value = 4
}

async function uploadDocumentOnly() {
  uploadError.value = ''
  uploading.value = true
  try {
    await uploadDocuments({
      documentKind: documentKind.value,
      documentFront: documentFrontFile.value,
      documentBack: documentKind.value === 'national_id' ? documentBackFile.value : null,
    })
    returnToVerificationReady()
  } catch (err) {
    uploadError.value = err.response?.data?.error || 'Document upload failed'
  } finally {
    uploading.value = false
  }
}

function onFrontPassed(file) {
  documentFrontFile.value = file
  if (documentKind.value === 'passport') {
    if (recaptureMode.value === 'document') {
      uploadDocumentOnly()
      return
    }
    currentStep.value = 3
  } else {
    docSubstep.value = 'back'
  }
}

function onBackPassed(file) {
  documentBackFile.value = file
  if (recaptureMode.value === 'document') {
    uploadDocumentOnly()
    return
  }
  currentStep.value = 3
}

function backFromSelfie() {
  if (recaptureMode.value === 'selfie') {
    currentStep.value = 4
    verificationPhase.value = 'failed'
    return
  }
  currentStep.value = 2
  docSubstep.value = documentKind.value === 'passport' ? 'front' : 'back'
}

async function onSelfiePassed({ file, challenge }) {
  selfieFile.value = file
  selfieChallenge.value = challenge
  uploadError.value = ''
  uploading.value = true

  try {
    if (recaptureMode.value === 'selfie') {
      await uploadDocuments({
        selfieImage: file,
        selfieChallenge: challenge,
      })
      returnToVerificationReady()
      return
    }

    await uploadDocuments({
      documentKind: documentKind.value,
      documentFront: documentFrontFile.value,
      documentBack: documentKind.value === 'national_id' ? documentBackFile.value : null,
      selfieImage: file,
      selfieChallenge: challenge,
    })
    recaptureMode.value = null
    verificationPhase.value = 'idle'
    qualityFailures.value = []
    failedImages.value = []
    verificationError.value = ''
    currentStep.value = 4
  } catch (err) {
    uploadError.value = err.response?.data?.error || 'Document upload failed'
  } finally {
    uploading.value = false
  }
}

function validateDateOfBirth(value) {
  if (!value) return 'Date of birth is required'
  const date = new Date(`${value}T00:00:00`)
  if (Number.isNaN(date.getTime())) return 'Enter a valid date of birth'
  const now = new Date()
  if (date >= now) return 'Date of birth must be in the past'
  const ageYears = (now - date) / (365.25 * 24 * 60 * 60 * 1000)
  if (ageYears < 18) return 'You must be at least 18 years old'
  if (ageYears > 120) return 'Enter a valid date of birth'
  return ''
}

function validatePersonalDetails() {
  let valid = true
  personalErrors.fullName = ''
  personalErrors.phoneNumber = ''
  personalErrors.nationalID = ''
  personalErrors.dateOfBirth = ''
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

  const dobError = validateDateOfBirth(personalForm.dateOfBirth)
  if (dobError) {
    personalErrors.dateOfBirth = dobError
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
      dateOfBirth: personalForm.dateOfBirth,
      deviceFingerprint: getDeviceFingerprint(),
    })
    currentStep.value = 2
    docSubstep.value = 'choose'
  } catch (err) {
    personalErrors.general = messageFromGuardrailError(err)
  } finally {
    savingDetails.value = false
  }
}

async function refreshVerificationStatus() {
  try {
    const status = await getVerificationStatus()
    if (status.pipeline) {
      pipelineState.value = { ...pipelineState.value, ...status.pipeline }
    }

    if (status.decision?.finalDecision) {
      finalDecision.value = status.decision.finalDecision
      verificationPhase.value = 'decision'
      pipelineState.value.verificationDecision = 'complete'
      stopPolling()
      return status
    }

    if (status.status === 'pending' || status.status === 'not_started') {
      // Keep current phase unless already decided
      if (verificationPhase.value !== 'loading' && verificationPhase.value !== 'failed') {
        verificationPhase.value = status.scores ? 'passed' : 'idle'
      }
    } else if (['verified', 'review', 'rejected'].includes(status.status)) {
      finalDecision.value = status.status
      verificationPhase.value = 'decision'
      stopPolling()
    }

    return status
  } catch {
    return null
  }
}

function startPollingIfNeeded() {
  stopPolling()
  pollTimer = setInterval(async () => {
    const status = await refreshVerificationStatus()
    if (status?.isFinal || ['verified', 'review', 'rejected'].includes(status?.status)) {
      stopPolling()
    }
  }, 5000)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

async function handleProceedToVerification() {
  verificationPhase.value = 'loading'
  verificationError.value = ''
  qualityFailures.value = []
  failedImages.value = []
  finalDecision.value = null
  pipelineState.value = {
    imageQuality: 'pending',
    documentVerification: 'pending',
    faceMatching: 'pending',
    livenessDetection: 'pending',
    verificationDecision: 'pending',
  }

  try {
    const result = await initiateVerification(getDeviceFingerprint())

    if (!result.overallPassed) {
      verificationPhase.value = 'failed'
      qualityFailures.value = result.failures || []
      failedImages.value = result.failedImages || []
      return
    }

    if (result.pipeline) {
      pipelineState.value = { ...pipelineState.value, ...result.pipeline }
    }

    if (result.finalDecision || result.decision?.finalDecision) {
      finalDecision.value = result.finalDecision || result.decision.finalDecision
      verificationPhase.value = 'decision'
      pipelineState.value.verificationDecision = 'complete'
      stopPolling()
      return
    }

    verificationPhase.value = 'passed'
    startPollingIfNeeded()
  } catch (err) {
    verificationPhase.value = 'idle'
    verificationError.value =
      err.response?.data?.error || err.message || 'Verification request failed'
  }
}

function handleReupload() {
  const needsDocument = failedImages.value.includes('document')
  const needsSelfie = failedImages.value.includes('selfie')
  verificationError.value = ''
  uploadError.value = ''

  if (needsSelfie && !needsDocument) {
    recaptureMode.value = 'selfie'
    selfieFile.value = null
    selfieChallenge.value = null
    verificationPhase.value = 'idle'
    currentStep.value = 3
    return
  }

  if (needsDocument && !needsSelfie) {
    recaptureMode.value = 'document'
    documentFrontFile.value = null
    documentBackFile.value = null
    docSubstep.value = 'front'
    verificationPhase.value = 'idle'
    currentStep.value = 2
    return
  }

  recaptureMode.value = 'both'
  documentFrontFile.value = null
  documentBackFile.value = null
  selfieFile.value = null
  selfieChallenge.value = null
  docSubstep.value = 'front'
  verificationPhase.value = 'idle'
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

.header-actions {
  display: flex;
  gap: 0.6rem;
  align-items: center;
}

.btn-link {
  text-decoration: none;
  color: #2b6cb0;
  font-weight: 600;
  font-size: 0.875rem;
  padding: 0.45rem 0.7rem;
  border-radius: 8px;
}

.btn-link:hover {
  background: #ebf8ff;
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

.recapture-note {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  background: #ebf8ff;
  border: 1px solid #90cdf4;
  color: #2a4365;
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

.field-hint {
  display: block;
  margin-top: 0.25rem;
  color: #627d98;
  font-size: 0.8125rem;
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

.doc-type-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 0.5rem;
}

.doc-type-card {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  text-align: left;
  padding: 1.1rem 1.15rem;
  border-radius: 12px;
  border: 1px solid #d9e2ec;
  background: #fff;
  cursor: pointer;
  color: #243b53;
}

.doc-type-card:hover {
  border-color: #3e7cb1;
  box-shadow: 0 0 0 3px rgba(62, 124, 177, 0.12);
}

.doc-type-card strong {
  font-size: 1.05rem;
}

.doc-type-card span {
  color: #627d98;
  font-size: 0.9rem;
}

.doc-type-grid .btn-secondary {
  grid-column: 1 / -1;
  justify-self: start;
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

.banner {
  margin: 1.25rem 0 1rem;
  padding: 0.9rem 1rem;
  border-radius: 10px;
  font-weight: 700;
}

.banner-success {
  background: #f0fff4;
  color: #276749;
}

.banner-review {
  background: #fffbeb;
  color: #975a16;
}

.banner-rejected {
  background: #fff5f5;
  color: #9b2c2c;
}

.support-link {
  display: inline-block;
  margin-top: 0.75rem;
  color: #3e7cb1;
  font-weight: 600;
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

  .doc-type-grid {
    grid-template-columns: 1fr;
  }
}
</style>
