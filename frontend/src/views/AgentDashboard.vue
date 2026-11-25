<template>
  <!-- Document submission waits until the agent's registration status has loaded. -->
  <div class="dashboard workspace">
    <header class="dashboard-header">
      <div>
        <h1>Identity overview</h1>
        <p class="welcome">Follow your registration from personal details to a verification decision.</p>
      </div>

    </header>

    <PasskeyPrompt :ready="passkeyReady" />
    <div class="dashboard-content">
      <div v-if="bootLoading" class="panel loading-panel">Loading your registration status...</div>

      <template v-else>
        <aside class="registration-rail" aria-label="Registration progress">
          <div class="record-holder">
            <span>Agent record</span>
            <strong>{{ displayName }}</strong>
          </div>
          <div class="step-heading">
            <h2>Registration steps</h2>
            <span>{{ currentStep }} / {{ stepLabels.length }}</span>
          </div>
          <ol class="registration-steps">
            <li v-for="(label, index) in stepLabels" :key="label"
                :aria-current="currentStep === index + 1 ? 'step' : undefined"
                :class="{ active: currentStep === index + 1, done: currentStep > index + 1 }">
              <span class="step-index"><Check v-if="currentStep > index + 1" :size="14" aria-label="Completed" /><template v-else>{{ index + 1 }}</template></span>
              <span>{{ label }}</span>
            </li>
          </ol>
        </aside>

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
              <span class="field-hint">Must match the date on your ID, passport, or driver's licence</span>
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
          <h2 v-if="docSubstep === 'choose'">Identity document</h2>
          <p v-if="recaptureMode === 'document'" class="panel-copy recapture-note">
            Your selfie is fine — only recapture the identity document that failed quality checks.
          </p>
          <p v-else-if="docSubstep === 'choose'" class="panel-copy">
            Choose the ID you have with you. We’ll check that each photo is readable before you continue.
          </p>

          <div v-if="docSubstep === 'choose'" class="doc-type-grid">
            <button v-for="doc in documents" :key="doc.id" type="button" class="doc-type-card" @click="selectDocKind(doc.id)">
              <img :src="doc.image" alt="" width="896" height="552" />
              <strong>{{ doc.name }}</strong><span>{{ doc.capture }}</span>
            </button>
            <button type="button" class="btn-secondary" @click="currentStep = 1">Back</button>
          </div>

          <DocumentCaptureStep
            v-else-if="docSubstep === 'front'"
            :title="frontCaptureTitle"
            :hint="frontCaptureHint"
            :initial-file="documentFrontFile"
            :document-kind="documentKind"
            :camera-only="documentCameraRequired"
            @back="onDocumentFrontBack"
            @passed="onFrontPassed"
          />

          <DocumentCaptureStep
            v-else-if="docSubstep === 'back'"
            title="ID back"
            hint="Capture the back of your national ID. The ID number must be readable so it can be matched to the front."
            :initial-file="documentBackFile"
            :document-kind="documentKind"
            :camera-only="documentCameraRequired"
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
            <div class="success-icon" aria-hidden="true"><Check :size="26" /></div>
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
            <div class="error-icon" aria-hidden="true"><CircleAlert :size="26" /></div>
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
            <template v-if="finalDecision === 'verified'">
              <h2 class="banner banner-success"><ShieldCheck :size="24" aria-hidden="true" />{{ adminReviewedAt ? 'Approved by admin' : 'Your identity has been verified' }}</h2>
              <p class="panel-copy">
                You now have full platform access. Continue to the agent workspace to get started.
              </p>
              <button type="button" class="btn-primary" @click="router.push('/agent/platform')">
                Proceed to Platform
              </button>
            </template>

            <template v-else-if="finalDecision === 'review'">
              <h2 class="banner banner-review"><Clock3 :size="24" aria-hidden="true" />Your verification is under review</h2>
              <p class="panel-copy">
                An administrator is reviewing your case. You will be notified once a decision is made.
                No further action is required from you right now.
              </p>
              <div v-if="feedback?.reasons?.length" class="feedback-block">
                <h3>Why it needs a review</h3>
                <ul class="reason-list">
                  <li v-for="reason in feedback.reasons" :key="reason">{{ reason }}</li>
                </ul>
              </div>
            </template>

            <template v-else-if="finalDecision === 'rejected'">
              <h2 class="banner banner-rejected"><CircleAlert :size="24" aria-hidden="true" />Your verification was unsuccessful</h2>
              <p v-if="adminReviewedAt" class="panel-copy">Rejected by admin</p>
              <p class="panel-copy">{{ feedback?.summary || 'Your identity could not be verified with the documents provided.' }}</p>

              <div v-if="feedback?.reasons?.length" class="feedback-block">
                <h3>What went wrong</h3>
                <ul class="reason-list">
                  <li v-for="reason in feedback.reasons" :key="reason">{{ reason }}</li>
                </ul>
              </div>

              <div v-if="feedback?.canRetry && feedback?.suggestions?.length" class="feedback-block tips">
                <h3>Before you try again</h3>
                <ul class="reason-list">
                  <li v-for="tip in feedback.suggestions" :key="tip">{{ tip }}</li>
                </ul>
              </div>

              <template v-if="feedback?.canRetry">
                <button type="button" class="btn-primary" @click="handleRetryVerification">
                  Try again ({{ feedback.attemptsRemaining }} of {{ feedback.maxAttempts }} attempts left)
                </button>
                <p class="score-note">
                  You will retake your document photos and selfie, then the checks run again.
                </p>
              </template>
              <template v-else>
                <p class="panel-copy">If you believe this is an error, please contact support.</p>
                <a class="support-link" href="mailto:support@example.com">Contact support</a>
              </template>
            </template>

            <template v-else>
              <div class="spinner" aria-hidden="true" />
              <h2>Finalising decision</h2>
              <p class="panel-copy">Waiting for the access control decision...</p>
            </template>

            <section v-if="feedback?.scores" class="score-panel" aria-labelledby="results-heading">
              <h3 id="results-heading">Your results</h3>
              <dl class="result-metrics">
                <div v-for="score in resultScores" :key="score.label" class="result-metric">
                  <dt>{{ score.label }}</dt>
                  <dd v-if="score.value !== null">
                    <span class="result-value">{{ scoreFormat.format(score.value) }}<small>%</small></span>
                    <span class="result-track" :class="score.band" role="meter" :aria-label="score.label"
                      aria-valuemin="0" aria-valuemax="100" :aria-valuenow="score.value"
                      :aria-valuetext="scoreFormat.format(score.value) + '% (' + score.band + ')'">
                      <span :style="{ width: score.value + '%' }"></span>
                    </span>
                  </dd>
                  <dd v-else class="missing-score">Unavailable</dd>
                </div>
              </dl>
            </section>

            <details class="check-details" :open="!finalDecision">
              <summary>Verification checks <ChevronDown :size="16" aria-hidden="true" /></summary>
              <ol class="pipeline-progress" aria-label="Verification checks">
                <li
                  v-for="step in pipelineSteps"
                  :key="step.label"
                  :class="step.complete ? 'complete' : 'pending-step'"
                >
                  <span>{{ step.label }}</span>
                  <span class="check-state"><Check v-if="step.complete" :size="14" aria-hidden="true" />{{ step.complete ? 'Complete' : 'Pending' }}</span>
                </li>
              </ol>
              <p v-if="feedback?.scores" class="score-note threshold-note">
                Reference thresholds are 70% for OCR confidence, 80% for face match, and 75% for liveness.
              </p>
            </details>
          </template>

          <p v-if="verificationError" class="error">{{ verificationError }}</p>
        </section>
      </template>
    </div>
  </div>
</template>

<script setup>
import { verificationScoreScales } from '../utils/verificationScoreScales.js'
import { documents } from '../utils/documentGuide.js'
import { Check, ChevronDown, CircleAlert, Clock3, ShieldCheck } from '@lucide/vue'
import PasskeyPrompt from '../components/PasskeyPrompt.vue'
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
const stepLabels = ['Personal details', 'Photo ID', 'Live selfie', 'Result']
const savingDetails = ref(false)
const uploading = ref(false)
const uploadError = ref('')
const email = ref('')

const documentKind = ref('national_id') // national_id | passport | drivers_licence
const docSubstep = ref('choose') // choose | front | back
const documentFrontFile = ref(null)
const documentBackFile = ref(null)
// Fail closed until the persisted attempt history has loaded.
const documentCameraRequired = ref(true)

const frontCaptureTitle = computed(() => {
  if (documentKind.value === 'passport') return 'Passport bio-data page'
  if (documentKind.value === 'drivers_licence') return "Driver's licence front"
  return 'ID front'
})

const frontCaptureHint = computed(() => {
  if (documentKind.value === 'passport') {
    return 'Open the passport to the page with your photo and lay it flat. Make sure the two lines of <<< text at the bottom are sharp and fully in the frame - the facing page may be in the shot.'
  }
  if (documentKind.value === 'drivers_licence') {
    return 'Capture the front of your licence. Surname, other names, national ID, date of birth, and expiry must be readable.'
  }
  return 'Capture the front of your national ID. Keep the name, ID number, and dates sharp and evenly lit.'
})

function needsDocumentBack(kind = documentKind.value) {
  return kind === 'national_id'
}
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
const adminReviewedAt = ref(null)
// Ask for a passkey only after the AI decision confirms the account.
const passkeyReady = computed(() =>
  !bootLoading.value
  && currentStep.value === 4
  && verificationPhase.value === 'decision'
  && finalDecision.value === 'verified'
)
// plain-language results from the backend: scores, reasons, whether a retry is allowed
const feedback = ref(null)
const scoreFormat = new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 })
const resultMetrics = [
  { key: 'ocrConfidenceScore', label: 'OCR confidence' },
  { key: 'faceMatchScore', label: 'Face match' },
  { key: 'livenessScore', label: 'Liveness' },
]
const resultScores = computed(() => resultMetrics.map(({ key, label }) => {
  const { max, amberThreshold, greenThreshold } = verificationScoreScales[key]
  const raw = feedback.value?.scores?.[key]
  const value = typeof raw === 'string' && raw.trim() ? Number(raw) : raw
  if (!Number.isFinite(value) || value < 0 || value > max) return { label, value: null }
  const band = value >= greenThreshold ? 'high' : value >= amberThreshold ? 'medium' : 'low'
  return { label, value: (value / max) * 100, band }
}))
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
    label: 'Image quality',
    complete: pipelineState.value.imageQuality === 'complete',
  },
  {
    label: 'Document verification',
    complete: pipelineState.value.documentVerification === 'complete',
  },
  {
    label: 'Face matching',
    complete: pipelineState.value.faceMatching === 'complete',
  },
  {
    label: 'Liveness detection',
    complete: pipelineState.value.livenessDetection === 'complete',
  },
  {
    label: 'Verification decision',
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

    const [{ status, documentCameraRequired: cameraRequired }, profile] = await Promise.all([
      getRegistrationStatus(),
      getProfile(),
    ])

    documentCameraRequired.value = cameraRequired !== false

    email.value = profile.email || email.value
    const savedDocument = profile.documents?.find(doc => ['id_front', 'passport', 'drivers_licence'].includes(doc.document_type))
    if (savedDocument) documentKind.value = savedDocument.document_type === 'id_front' ? 'national_id' : savedDocument.document_type

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
      documentBack: needsDocumentBack() ? documentBackFile.value : null,
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
  if (needsDocumentBack()) {
    docSubstep.value = 'back'
    return
  }
  if (recaptureMode.value === 'document') {
    uploadDocumentOnly()
    return
  }
  currentStep.value = 3
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
  docSubstep.value = needsDocumentBack() ? 'back' : 'front'
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
      documentBack: needsDocumentBack() ? documentBackFile.value : null,
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
    adminReviewedAt.value = status.decision?.adminReviewedAt || null
    if (status.pipeline) {
      pipelineState.value = { ...pipelineState.value, ...status.pipeline }
    }
    if (status.feedback) {
      feedback.value = status.feedback
    }

    if (status.decision?.finalDecision) {
      finalDecision.value = status.decision.finalDecision
      verificationPhase.value = 'decision'
      pipelineState.value.verificationDecision = 'complete'
      if (finalDecision.value !== 'review') stopPolling()
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
      if (finalDecision.value !== 'review') stopPolling()
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
    if (['verified', 'rejected'].includes(status?.status)) {
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
  adminReviewedAt.value = null
  feedback.value = null
  pipelineState.value = {
    imageQuality: 'pending',
    documentVerification: 'pending',
    faceMatching: 'pending',
    livenessDetection: 'pending',
    verificationDecision: 'pending',
  }

  try {
    const result = await initiateVerification(getDeviceFingerprint())
    documentCameraRequired.value = true

    if (!result.overallPassed) {
      verificationPhase.value = 'failed'
      qualityFailures.value = result.failures || []
      failedImages.value = result.failedImages || []
      return
    }

    if (result.pipeline) {
      pipelineState.value = { ...pipelineState.value, ...result.pipeline }
    }
    if (result.feedback) {
      feedback.value = result.feedback
    }

    if (result.finalDecision || result.decision?.finalDecision) {
      finalDecision.value = result.finalDecision || result.decision.finalDecision
      verificationPhase.value = 'decision'
      pipelineState.value.verificationDecision = 'complete'
      if (finalDecision.value === 'review') startPollingIfNeeded()
      else stopPolling()
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

/** Borderline rejection: start over from the document capture with fresh photos. */
function handleRetryVerification() {
  stopPolling()
  finalDecision.value = null
  adminReviewedAt.value = null
  feedback.value = null
  failedImages.value = ['document', 'selfie']
  handleReupload()
}

function handleReupload() {
  documentCameraRequired.value = true
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
  background: linear-gradient(180deg, var(--canvas) 0%, var(--surface-muted) 40%, var(--surface-muted) 100%);
}

.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 2rem;
  background: rgba(255, 255, 255, 0.9);
  border-bottom: 1px solid var(--line);
}

.header-actions {
  display: flex;
  gap: 0.6rem;
  align-items: center;
}

.btn-link {
  text-decoration: none;
  color: var(--info);
  font-weight: 600;
  font-size: 0.875rem;
  padding: 0.45rem 0.7rem;
  border-radius: 8px;
}

.btn-link:hover {
  background: var(--info-bg);
}

h1 {
  font-size: 1.25rem;
  color: var(--ink);
}

.welcome {
  color: var(--muted);
  font-size: 0.875rem;
  margin-top: 0.15rem;
}

.btn-logout {
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid var(--line);
  border-radius: 8px;
  color: var(--ink);
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-logout:hover {
  background: var(--surface-muted);
}

.dashboard-content {
  padding: 2rem;
  max-width: 920px;
  margin: 0 auto;
}

/* Keep the active task wide enough for a camera preview or a two-column form. */
.dashboard { container-type:inline-size; }
.dashboard-content { display:grid; grid-template-columns:minmax(0,1fr) minmax(208px,.36fr); gap:20px; align-items:start; }
.dashboard-content > .panel { grid-column:1; grid-row:1; min-width:0; }
.dashboard-content > .loading-panel { grid-column:1 / -1; }
.registration-rail { grid-column:2; grid-row:1; overflow:hidden; color:var(--ink); background:var(--surface); border:1px solid var(--line); border-radius:12px; }
.record-holder { position:relative; isolation:isolate; overflow:hidden; min-height:128px; display:flex; flex-direction:column; justify-content:flex-end; gap:8px; padding:20px; background:#131b16; color:#f3f6ef; }
.record-holder::before { content:""; position:absolute; z-index:-1; inset:0 0 0 36%; background:url("/fingerprint-study.webp") right center / cover no-repeat; opacity:.26; mask-image:linear-gradient(to right,transparent,#000); }
.record-holder span,.step-heading span { font:12px/1.5 var(--meta-font); }
.record-holder span { color:#c9d5c8; }
.record-holder strong { font-size:clamp(20px,2vw,28px); line-height:1.15; letter-spacing:-.035em; font-weight:500; overflow-wrap:anywhere; }
.step-heading { display:flex; gap:12px; align-items:center; justify-content:space-between; margin:20px 16px 12px; }
#app .step-heading h2 { font-size:14px; font-weight:550; }
.step-heading span { color:var(--muted); white-space:nowrap; }
.registration-steps { list-style:none; display:grid; gap:4px; margin:0 8px 12px; }
.registration-steps li { display:flex; align-items:center; gap:12px; min-height:42px; padding:8px; color:var(--muted); font-size:14px; border-radius:6px; }
.registration-steps .active { color:var(--selected-text); background:var(--selected-bg); font-weight:600; }
.step-index { flex:none; width:24px; height:24px; display:grid; place-items:center; border:1px solid var(--line); border-radius:50%; font:12px var(--meta-font); }
.active .step-index { color:var(--on-brand); background:var(--action); border-color:var(--action); }
.done .step-index { color:var(--success); background:var(--success-bg); border-color:var(--success-border); }
#app .dashboard .dashboard-content > .panel { padding:clamp(20px,2.5vw,36px); }
#app .dashboard .dashboard-content > .panel > h2 { font-size:clamp(24px,2.4vw,36px); letter-spacing:-.045em; line-height:1.12; font-weight:500; }
#app .dashboard .panel-copy { font-size:14px; line-height:1.6; }
#app .dashboard .form input { border-color:var(--input-border); }
#app .dashboard .form input:read-only { background:var(--surface-muted); }
@container (max-width:820px) {
  .dashboard-content { grid-template-columns:minmax(0,1fr); gap:16px; }
  .registration-rail,.dashboard-content > .panel { grid-column:auto; grid-row:auto; }
  .record-holder { min-height:0; padding:12px 16px; flex-direction:row; align-items:baseline; justify-content:space-between; }
  .record-holder strong { font-size:18px; text-align:right; }
  .step-heading { margin:12px 16px 4px; }
  .registration-steps { grid-template-columns:repeat(4,minmax(0,1fr)); margin-bottom:8px; }
  .registration-steps li { font-size:12px; gap:6px; }
}
@container (max-width:550px) {
  .registration-steps { grid-template-columns:repeat(2,minmax(0,1fr)); }
  .registration-steps li { min-height:32px; padding:4px 8px; }
}

.panel {
  background: var(--surface);
  border-radius: 14px;
  padding: 2rem;
  box-shadow: 0 2px 14px rgba(15, 23, 42, 0.06);
}

.loading-panel {
  text-align: center;
  color: var(--muted);
}

h2 {
  font-size: 1.35rem;
  color: var(--ink);
  margin-bottom: 0.35rem;
}

.panel-copy {
  color: var(--muted);
  margin-bottom: 1.5rem;
  line-height: 1.55;
}

.recapture-note {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  background: var(--info-bg);
  border: 1px solid var(--info-border);
  color: var(--info);
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
  color: var(--ink);
}

input {
  padding: 0.7rem 0.85rem;
  border: 1px solid var(--line);
  border-radius: 8px;
  font-size: 0.95rem;
}

input:focus {
  outline: none;
  border-color: var(--action);
  box-shadow: 0 0 0 3px var(--focus-ring);
}

input[readonly] {
  background: var(--surface-muted);
  color: var(--ink);
}

.field-hint {
  display: block;
  margin-top: 0.25rem;
  color: var(--muted);
  font-size: 0.8125rem;
}

.field-error,
.error {
  color: var(--danger);
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
  background: var(--action);
  color: var(--on-brand);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary:hover:not(:disabled) {
  background: var(--action-hover);
}

.btn-secondary {
  background: var(--surface);
  color: var(--ink);
  border: 1px solid var(--line);
}

.doc-type-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit,minmax(min(100%,148px),1fr));
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
  border: 1px solid var(--line);
  background: var(--surface);
  cursor: pointer;
  color: var(--ink);
}

.doc-type-card:hover {
  border-color: var(--action);
  box-shadow: 0 0 0 3px var(--focus-ring);
}

.doc-type-card img { width:100%; aspect-ratio:896/552; height:auto; object-fit:contain; background:#739d92; border-radius:6px; margin-bottom:6px; }

.doc-type-card strong {
  font-size: 1.05rem;
}

.doc-type-card span {
  color: var(--muted);
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

.confirmation { text-align:left; }

.success-icon {
  width: 56px;
  height: 56px;
  margin: 0 0 1rem;
  border-radius: 50%;
  background: var(--success-bg);
  color: var(--success);
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
  background: var(--success-bg);
  color: var(--success);
}

.status-list li.pending {
  background: var(--warning-bg);
  color: var(--warning);
}

.proceed-btn {
  margin-top: 1.5rem;
}

.spinner {
  width: 48px;
  height: 48px;
  margin: 0 0 1.25rem;
  border: 4px solid var(--line);
  border-top-color: var(--action);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@media (prefers-reduced-motion:reduce) { .spinner { animation:none; } }

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-icon {
  width: 56px;
  height: 56px;
  margin: 0 0 1rem;
  border-radius: 50%;
  background: var(--danger-bg);
  color: var(--danger);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
}

.failure-list {
  list-style: none;
  text-align: left;
  margin: 0 0 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.failure-list li {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  background: var(--danger-bg);
  color: var(--danger);
  font-size: 0.9rem;
  font-weight: 500;
}

.score-panel {
  container-type:inline-size;
  margin-top:24px;
  padding:clamp(16px,2vw,28px);
  border:1px solid #39463e;
  border-radius:12px;
  background:#18211b;
  color:#f2f6ee;
}
#app .score-panel h3 { margin:0; color:inherit; font-size:20px; font-weight:500; letter-spacing:-.025em; }
.result-metrics { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); margin:20px 0 0; }
.result-metric { min-width:0; padding:0 16px; border-inline-start:1px solid #435047; }
.result-metric:first-child { padding-inline-start:0; border:0; }
.result-metric:last-child { padding-inline-end:0; }
.result-metric dt { color:#c4d0c5; font-size:14px; }
.result-metric dd { margin:4px 0 0; }
.result-value { display:block; font:500 clamp(24px,5.2cqi,42px)/1.25 var(--ui-font); letter-spacing:-.04em; font-variant-numeric:tabular-nums; }
.result-value small { margin-inline-start:2px; color:#c4d0c5; font-size:.52em; letter-spacing:0; }
.result-track { display:block; height:5px; margin-top:14px; overflow:hidden; border-radius:2px; background:#455248; }
.result-track.low { color:#ff8880; }
.result-track.medium { color:#ffb45e; }
.result-track.high { color:#77dc92; }
.result-track > span { display:block; height:100%; background:currentColor; }
.result-track[aria-valuenow="0"] { border-inline-start:2px solid currentColor; }
.result-metric .missing-score { color:#c4d0c5; font-size:14px; margin-top:12px; }
@container (max-width:425px) {
  .result-metrics { display:block; margin-top:12px; }
  .result-metric,.result-metric:first-child { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:12px; align-items:center; padding:12px 0; border:0; border-top:1px solid #435047; }
  .result-metric:last-child { padding-bottom:0; }
  .result-metric dd,.result-metric .missing-score { margin:0; text-align:right; }
  .result-track { margin-top:6px; }
}

.feedback-block h3 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
}

.score-note {
  margin: 0;
  font-size: 0.8rem;
  color: var(--muted);
}

.feedback-block {
  margin: 1rem 0;
  padding: 0.9rem 1rem;
  border-radius: 10px;

  border: 1px solid var(--warning-border);
 background:var(--warning-bg); color:var(--warning); border-color:var(--warning-border); }

.feedback-block.tips {


 background:var(--info-bg); color:var(--info); border-color:var(--info-border); }

.reason-list {
  margin: 0.5rem 0 0;
  padding-left: 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.9rem;
  line-height: 1.4;
}

.check-details { margin-top:20px; border-block:1px solid var(--line); }
.check-details summary { display:flex; justify-content:space-between; align-items:center; padding:12px 0; font-size:14px; font-weight:500; cursor:pointer; list-style:none; }
.check-details summary::-webkit-details-marker { display:none; }
.check-details[open] summary svg { transform:rotate(180deg); }
.pipeline-progress { list-style:none; padding:0; margin:0; border-top:1px solid var(--line); }
.pipeline-progress li { display:flex; align-items:center; justify-content:space-between; gap:16px; min-height:40px; padding:8px 0; border-bottom:1px solid var(--line); font-size:14px; }
.pipeline-progress li:last-child { border-bottom:0; }
.threshold-note { padding:8px 0 12px; }
.check-state { display:inline-flex; align-items:center; gap:6px; font-size:12px; }
.complete .check-state { color:var(--success); }
.pending-step .check-state { color:var(--warning); }
.banner {
  display:flex; align-items:center; gap:12px;
  margin: 0 0 1rem;
  padding: 1rem;
  border-radius: 10px;
  font-weight: 700;
}

.banner svg { flex:none; }
#app .dashboard .banner-success {
  background: var(--success-bg);
  color: var(--success);
}

#app .dashboard .banner-review {
  background: var(--warning-bg);
  color: var(--warning);
}

#app .dashboard .banner-rejected {
  background: var(--danger-bg);
  color: var(--danger);
}

.support-link {
  display: inline-block;
  margin-top: 0.75rem;
  color: var(--link);
  font-weight: 600;
}

@media (max-width: 768px) {
  .dashboard-content {
    padding: 1rem;
  }


  .upload-grid {
    grid-template-columns: 1fr;
  }

  .doc-type-grid {
    grid-template-columns: 1fr;
  }
}
</style>
