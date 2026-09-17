<template>
  <div class="admin">
    <header class="admin-header">
      <div>
        <h1>Admin Dashboard</h1>
        <p class="welcome">Signed in as {{ state.user?.email || 'Administrator' }}</p>
      </div>
      <button class="btn-logout" @click="handleLogout">Sign Out</button>
    </header>

    <!-- Real-time toast -->
    <Transition name="toast">
      <div v-if="toast.visible" class="toast" role="status">
        <div>
          <p class="toast-title">New case awaiting review</p>
          <p class="toast-body">{{ toast.agentName }}</p>
        </div>
        <button class="btn approve" @click="viewToastCase">View Case</button>
      </div>
    </Transition>

    <main class="admin-content">
      <!-- Stats bar -->
      <section class="stats-bar">
        <article class="stat-card">
          <div class="stat-icon total" aria-hidden="true">TA</div>
          <div>
            <p class="stat-label">Total Agents</p>
            <p class="stat-value">{{ stats.totalAgents }}</p>
          </div>
        </article>
        <article class="stat-card clickable amber" @click="goToPending">
          <div class="stat-icon amber" aria-hidden="true">AR</div>
          <div>
            <p class="stat-label">Awaiting Review</p>
            <p class="stat-value">{{ stats.awaitingReview }}</p>
          </div>
        </article>
        <article class="stat-card green">
          <div class="stat-icon green" aria-hidden="true">VT</div>
          <div>
            <p class="stat-label">Verified Today</p>
            <p class="stat-value">{{ stats.verifiedToday }}</p>
          </div>
        </article>
        <article class="stat-card red">
          <div class="stat-icon red" aria-hidden="true">RT</div>
          <div>
            <p class="stat-label">Rejected Today</p>
            <p class="stat-value">{{ stats.rejectedToday }}</p>
          </div>
        </article>
        <article class="stat-card grey">
          <div class="stat-icon grey" aria-hidden="true">PV</div>
          <div>
            <p class="stat-label">Pending Verification</p>
            <p class="stat-value">{{ stats.pendingVerification }}</p>
          </div>
        </article>
      </section>

      <!-- Recent activity -->
      <section class="panel activity-panel">
        <div class="toolbar">
          <h2>Recent activity</h2>
          <span class="muted">Auto-refreshes every 30s</span>
        </div>
        <ul class="activity-list">
          <li v-for="entry in recentActivity" :key="entry.logId">
            <span class="activity-time">{{ formatDate(entry.timestamp) }}</span>
            <span class="activity-name">{{ entry.agentName }}</span>
            <span class="activity-action">{{ entry.action }}</span>
            <span class="activity-outcome">{{ entry.outcome }}</span>
          </li>
          <li v-if="!recentActivity.length" class="empty">No recent activity.</li>
        </ul>
      </section>

      <nav class="tabs">
        <button :class="{ active: tab === 'pending' }" @click="switchTab('pending')">Pending review</button>
        <button :class="{ active: tab === 'agents' }" @click="switchTab('agents')">All agents</button>
        <button :class="{ active: tab === 'flagged' }" @click="switchTab('flagged')">Flagged registrations</button>
        <button :class="{ active: tab === 'audit' }" @click="switchTab('audit')">Audit log</button>
      </nav>

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="loading" class="muted">Loading...</p>

      <!-- Pending review -->
      <section v-if="tab === 'pending'" id="pending-section" class="panel">
        <h2>Pending review cases</h2>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Agent Name</th>
                <th>National ID</th>
                <th>Submission Date</th>
                <th>Face Match</th>
                <th>Liveness</th>
                <th>OCR</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in pendingCases" :key="item.request.request_id">
                <td>
                  <button class="linkish" @click="openDetail(item.agent.agent_id)">
                    {{ item.agent?.full_name || '—' }}
                  </button>
                </td>
                <td>{{ item.agent?.national_id || '—' }}</td>
                <td>{{ formatDate(item.request.created_at) }}</td>
                <td>{{ formatScore(item.scores?.face_match_score) }}</td>
                <td>{{ formatScore(item.scores?.liveness_score) }}</td>
                <td>{{ formatScore(item.scores?.ocr_confidence_score) }}</td>
                <td class="actions">
                  <button class="btn approve" @click="handleApprove(item)">Approve</button>
                  <button class="btn reject" @click="openRejectModal(item)">Reject</button>
                  <button class="btn ghost" @click="openDetail(item.agent.agent_id)">View</button>
                </td>
              </tr>
              <tr v-if="!pendingCases.length && !loading">
                <td colspan="7" class="empty">No cases awaiting review.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- All agents -->
      <section v-if="tab === 'agents'" class="panel">
        <div class="toolbar">
          <h2>All agents</h2>
          <div class="filters">
            <input v-model="search" type="search" placeholder="Search name or national ID" />
            <select v-model="statusFilter" @change="loadAgents">
              <option value="">All statuses</option>
              <option value="verified">Verified</option>
              <option value="review">Review</option>
              <option value="rejected">Rejected</option>
              <option value="pending">Pending</option>
            </select>
          </div>
        </div>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Agent Name</th>
                <th>National ID</th>
                <th>Status</th>
                <th>Submission Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in filteredAgents"
                :key="item.agent.agent_id"
                class="clickable"
                @click="openDetail(item.agent.agent_id)"
              >
                <td>{{ item.agent.full_name }}</td>
                <td>{{ item.agent.national_id }}</td>
                <td><span class="badge" :class="item.status">{{ item.status }}</span></td>
                <td>{{ formatDate(item.request?.created_at || item.agent.created_at) }}</td>
                <td><button class="btn ghost" @click.stop="openDetail(item.agent.agent_id)">View</button></td>
              </tr>
              <tr v-if="!filteredAgents.length && !loading">
                <td colspan="5" class="empty">No agents found.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Flagged registrations -->
      <section v-if="tab === 'flagged'" class="panel">
        <div class="toolbar">
          <h2>Flagged registrations</h2>
          <span class="muted">Last 7 days · {{ flaggedTotal }} events</span>
        </div>

        <div v-if="flaggedGroups.length" class="flagged-groups">
          <article v-for="group in flaggedGroups" :key="group.ipAddress" class="ip-group">
            <header>
              <strong>{{ group.ipAddress }}</strong>
              <span class="badge review">{{ group.count }} blocked attempt{{ group.count === 1 ? '' : 's' }}</span>
            </header>
          </article>
        </div>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>IP Address</th>
                <th>Device Fingerprint</th>
                <th>Guardrail Type</th>
                <th>Attempt Count</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="entry in flaggedEntries" :key="entry.logId">
                <td>{{ formatDate(entry.timestamp) }}</td>
                <td>{{ entry.ipAddress || '—' }}</td>
                <td class="mono">{{ truncateFingerprint(entry.deviceFingerprint) }}</td>
                <td>
                  <span class="badge" :class="guardrailBadgeClass(entry.guardrailType)">
                    {{ formatGuardrail(entry.guardrailType) }}
                  </span>
                </td>
                <td>{{ entry.attemptCount ?? '—' }}</td>
              </tr>
              <tr v-if="!flaggedEntries.length && !loading">
                <td colspan="5" class="empty">No flagged registrations in the last 7 days.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Audit logs -->
      <section v-if="tab === 'audit'" class="panel">
        <div class="toolbar">
          <h2>Audit log</h2>
          <div class="filters">
            <button class="btn ghost" @click="exportModal.open = true">Export Audit Logs</button>
            <button class="btn ghost" :disabled="auditPage <= 1" @click="changeAuditPage(-1)">Previous</button>
            <span class="muted">Page {{ auditPage }}</span>
            <button class="btn ghost" :disabled="auditPage * 20 >= auditTotal" @click="changeAuditPage(1)">Next</button>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th class="sortable" @click="toggleAuditSort">Timestamp {{ auditSortAsc ? '↑' : '↓' }}</th>
                <th>Agent Name</th>
                <th>Action</th>
                <th>Outcome</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in sortedAuditLogs" :key="log.logId">
                <td>{{ formatDate(log.timestamp) }}</td>
                <td>{{ log.agentName }}</td>
                <td>{{ log.action }}</td>
                <td>{{ log.outcome }}</td>
              </tr>
              <tr v-if="!sortedAuditLogs.length && !loading">
                <td colspan="4" class="empty">No audit entries yet.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>

    <!-- Reject modal -->
    <div v-if="rejectModal.open" class="modal-backdrop">
      <div class="modal">
        <h3>Reject agent</h3>
        <p>Optionally provide a reason for rejection.</p>
        <textarea v-model="rejectModal.reason" rows="4" placeholder="Rejection reason" />
        <div class="modal-actions">
          <button class="btn ghost" @click="rejectModal.open = false">Cancel</button>
          <button class="btn reject" @click="confirmReject">Reject</button>
        </div>
      </div>
    </div>

    <!-- Export modal -->
    <div v-if="exportModal.open" class="modal-backdrop">
      <div class="modal">
        <h3>Export Audit Logs</h3>
        <label class="field">
          <span>Start date</span>
          <input v-model="exportModal.startDate" type="date" />
        </label>
        <label class="field">
          <span>End date</span>
          <input v-model="exportModal.endDate" type="date" />
        </label>
        <label class="field">
          <span>Agent name (optional)</span>
          <input v-model="exportModal.agentName" type="text" placeholder="Search by agent name" />
        </label>
        <p v-if="exportModal.error" class="error">{{ exportModal.error }}</p>
        <div class="modal-actions">
          <button class="btn ghost" :disabled="exportModal.loading" @click="exportModal.open = false">Cancel</button>
          <button class="btn approve" :disabled="exportModal.loading" @click="submitExport">
            {{ exportModal.loading ? 'Exporting…' : 'Download CSV' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Agent detail drawer -->
    <div v-if="detail" class="drawer-backdrop" @click.self="closeDetail">
      <aside class="drawer">
        <header>
          <h3>Agent detail</h3>
          <button class="btn ghost" @click="closeDetail">Close</button>
        </header>

        <section class="drawer-section">
          <h4>Agent information</h4>
          <dl class="info-grid">
            <div><dt>Full name</dt><dd>{{ detail.agent.full_name }}</dd></div>
            <div><dt>Email</dt><dd>{{ detail.agent.email || '—' }}</dd></div>
            <div><dt>Phone</dt><dd>{{ detail.agent.phone_number || '—' }}</dd></div>
            <div><dt>National ID</dt><dd>{{ detail.agent.national_id }}</dd></div>
            <div><dt>Date of birth</dt><dd>{{ formatDateOfBirth(detail.agent.date_of_birth) }}</dd></div>
            <div><dt>Registered</dt><dd>{{ formatDate(detail.agent.created_at) }}</dd></div>
          </dl>
        </section>

        <section class="drawer-section">
          <h4>Document images</h4>
          <div v-if="imagesLoading" class="image-grid">
            <div class="skeleton" />
            <div class="skeleton" />
          </div>
          <p v-else-if="imagesError" class="muted">{{ imagesError }}</p>
          <div v-else class="image-grid">
            <div>
              <p class="img-label">Identity document</p>
              <Lightbox
                v-if="documentUrl"
                :images="lightboxImages"
                :start-index="0"
                alt="Identity document"
              />
              <p v-else class="muted">Document image unavailable.</p>
            </div>
            <div v-if="documentBackUrl">
              <p class="img-label">ID back</p>
              <Lightbox
                :images="lightboxImages"
                :start-index="Math.min(1, lightboxImages.length - 1)"
                alt="ID back"
              />
            </div>
            <div>
              <p class="img-label">Selfie</p>
              <Lightbox
                v-if="selfieUrl"
                :images="lightboxImages"
                :start-index="Math.max(0, lightboxImages.length - 1)"
                alt="Selfie"
              />
              <p v-else class="muted">Selfie image unavailable.</p>
            </div>
          </div>
        </section>

        <section class="drawer-section">
          <h4>OCR extraction</h4>
          <div v-if="latestOcr" class="ocr-panel">
            <p class="muted ocr-note">
              Text read from the identity document vs what the agent registered.
            </p>
            <dl class="detail-grid ocr-grid">
              <div>
                <dt>Extracted name</dt>
                <dd>{{ latestOcr.extractedName || '—' }}</dd>
              </div>
              <div>
                <dt>Registered name</dt>
                <dd>{{ latestOcr.registeredName || '—' }}</dd>
              </div>
              <div>
                <dt>Extracted ID</dt>
                <dd>{{ latestOcr.extractedIDNumber || '—' }}</dd>
              </div>
              <div>
                <dt>Registered ID</dt>
                <dd>{{ latestOcr.registeredIDNumber || '—' }}</dd>
              </div>
              <div>
                <dt>Extracted DOB</dt>
                <dd>{{ latestOcr.extractedDOB || '—' }}</dd>
              </div>
              <div>
                <dt>Registered DOB</dt>
                <dd>{{ formatDateOfBirth(latestOcr.registeredDOB) }}</dd>
              </div>
            </dl>
            <div class="ocr-matches">
              <span class="match-pill" :class="latestOcr.nameMatch ? 'ok' : 'bad'">
                Name {{ latestOcr.nameMatch ? 'match' : 'mismatch' }}
              </span>
              <span class="match-pill" :class="latestOcr.idMatch ? 'ok' : 'bad'">
                ID {{ latestOcr.idMatch ? 'match' : 'mismatch' }}
              </span>
              <span class="match-pill" :class="latestOcr.dobMatch ? 'ok' : 'bad'">
                DOB {{ latestOcr.dobMatch ? 'match' : 'mismatch' }}
              </span>
            </div>
            <details v-if="latestOcr.rawText?.length" class="details-viewer">
              <summary>All OCR text ({{ latestOcr.rawText.length }} lines)</summary>
              <ul class="raw-text-list">
                <li v-for="(line, idx) in latestOcr.rawText" :key="idx">{{ line }}</li>
              </ul>
            </details>
          </div>
          <p v-else class="muted">
            No OCR extraction recorded yet. Re-run verification to capture document text.
          </p>
        </section>

        <section class="drawer-section">
          <h4>Verification scores</h4>
          <div v-if="latestScores" class="scores">
            <ScoreBar
              label="Face match"
              :value="num(latestScores.face_match_score)"
              :max="100"
              :green-threshold="80"
              :amber-threshold="50"
            />
            <ScoreBar
              label="Liveness"
              :value="num(latestScores.liveness_score)"
              :max="1"
              :green-threshold="0.75"
              :amber-threshold="0.5"
            />
            <ScoreBar
              label="OCR confidence"
              :value="num(latestScores.ocr_confidence_score)"
              :max="1"
              :green-threshold="0.7"
              :amber-threshold="0.4"
            />
            <ScoreBar
              label="Blur"
              :value="num(latestScores.blur_score)"
              :max="100"
              :green-threshold="80"
              :amber-threshold="50"
            />
            <ScoreBar
              label="Brightness"
              :value="num(latestScores.brightness_score)"
              :max="255"
              :green-threshold="220"
              :amber-threshold="40"
              range-mode
            />
            <ScoreBar
              label="Contrast"
              :value="num(latestScores.contrast_score)"
              :max="100"
              :green-threshold="30"
              :amber-threshold="15"
            />
          </div>
          <p v-else class="muted">No scores available.</p>
        </section>

        <section class="drawer-section">
          <h4>Decision</h4>
          <div v-if="latestRequest" class="decision-block">
            <span class="badge" :class="latestRequest.status">{{ latestRequest.status }}</span>
            <p v-if="latestDecision?.decided_at" class="muted">
              Decided {{ formatDate(latestDecision.decided_at) }}
              <span v-if="latestDecision.decision_basis"> · {{ latestDecision.decision_basis }}</span>
            </p>
            <div v-if="latestRequest.status === 'review'" class="actions">
              <button class="btn approve" @click="handleApproveFromDetail">Approve</button>
              <button class="btn reject" @click="openRejectFromDetail">Reject</button>
            </div>
            <div class="actions">
              <button class="btn ghost" :disabled="resettingStrikes" @click="handleResetStrikes">
                {{ resettingStrikes ? 'Resetting…' : 'Reset strikes' }}
              </button>
            </div>
            <p v-if="strikeMessage" class="muted">{{ strikeMessage }}</p>
            <p v-else-if="latestRequest.status !== 'review'" class="muted">Decision is read-only for this status.</p>
          </div>
          <p v-else class="muted">No verification request found.</p>
        </section>

        <section class="drawer-section">
          <h4>Audit log</h4>
          <p v-if="agentAuditLoading" class="muted">Loading audit log...</p>
          <ul v-else class="history-list">
            <li v-for="log in agentAuditLogs" :key="log.logId" class="audit-entry">
              <div class="audit-top">
                <strong>{{ formatDate(log.timestamp) }}</strong>
                <span class="muted">{{ log.performedByLabel || 'System' }}</span>
              </div>
              <div>{{ log.action }}: {{ log.outcome }}</div>
              <details v-if="log.details" class="details-viewer">
                <summary>View details</summary>
                <pre>{{ formatDetails(log.details) }}</pre>
              </details>
            </li>
            <li v-if="!agentAuditLogs.length" class="empty">No audit entries for this agent.</li>
          </ul>
        </section>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'
import Lightbox from '../components/Lightbox.vue'
import ScoreBar from '../components/ScoreBar.vue'
import {
  getPendingCases,
  getAllAgents,
  getAgentDetail,
  getAgentImages,
  getAgentAuditLogs,
  getFlaggedRegistrations,
  resetAgentStrikes,
  getDashboardStats,
  getRecentActivity,
  approveAgent,
  rejectAgent,
  getAuditLogs,
  exportAuditLogs,
} from '../services/adminService.js'
import { connectAdminSocket, disconnectAdminSocket } from '../services/socket.js'

const router = useRouter()
const { state, logout } = useAuthStore()

const tab = ref('overview')
const loading = ref(false)
const error = ref('')
const pendingCases = ref([])
const agents = ref([])
const search = ref('')
const statusFilter = ref('')
const detail = ref(null)
const auditLogs = ref([])
const auditPage = ref(1)
const auditTotal = ref(0)
const auditSortAsc = ref(false)
const recentActivity = ref([])
const imagesLoading = ref(false)
const imagesError = ref('')
const documentUrl = ref('')
const documentBackUrl = ref('')
const selfieUrl = ref('')
const agentAuditLogs = ref([])
const agentAuditLoading = ref(false)
const flaggedEntries = ref([])
const flaggedGroups = ref([])
const flaggedTotal = ref(0)
const resettingStrikes = ref(false)
const strikeMessage = ref('')
let activityTimer = null
let toastTimer = null
let socket = null

const stats = reactive({
  totalAgents: 0,
  awaitingReview: 0,
  verifiedToday: 0,
  rejectedToday: 0,
  pendingVerification: 0,
})

const toast = reactive({
  visible: false,
  agentName: '',
  agentId: null,
})

const rejectModal = reactive({
  open: false,
  item: null,
  reason: '',
})

const exportModal = reactive({
  open: false,
  startDate: '',
  endDate: '',
  agentName: '',
  loading: false,
  error: '',
})

const filteredAgents = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return agents.value
  return agents.value.filter((item) => {
    const name = item.agent.full_name?.toLowerCase() || ''
    const nid = item.agent.national_id?.toLowerCase() || ''
    return name.includes(q) || nid.includes(q)
  })
})

const sortedAuditLogs = computed(() => {
  const logs = [...auditLogs.value]
  logs.sort((a, b) => {
    const ta = new Date(a.timestamp).getTime()
    const tb = new Date(b.timestamp).getTime()
    return auditSortAsc.value ? ta - tb : tb - ta
  })
  return logs
})

const latestScores = computed(() => detail.value?.history?.[0]?.scores || null)
const latestRequest = computed(() => detail.value?.history?.[0]?.request || null)
const latestDecision = computed(() => detail.value?.history?.[0]?.decision || null)
const latestOcr = computed(() => detail.value?.latestOcr || null)

const lightboxImages = computed(() => {
  const images = []
  if (documentUrl.value) images.push({ url: documentUrl.value, alt: 'Identity document' })
  if (documentBackUrl.value) images.push({ url: documentBackUrl.value, alt: 'ID back' })
  if (selfieUrl.value) images.push({ url: selfieUrl.value, alt: 'Selfie' })
  return images
})

onMounted(async () => {
  tab.value = 'pending'
  await Promise.all([loadStats(), loadRecentActivity(), loadPending()])
  activityTimer = setInterval(loadRecentActivity, 30000)

  socket = connectAdminSocket()
  socket.on('new_review_case', onNewReviewCase)
})

onBeforeUnmount(() => {
  if (activityTimer) clearInterval(activityTimer)
  if (toastTimer) clearTimeout(toastTimer)
  if (socket) {
    socket.off('new_review_case', onNewReviewCase)
  }
  disconnectAdminSocket()
})

function onNewReviewCase(payload) {
  toast.agentName = payload.agentName || 'Unknown agent'
  toast.agentId = payload.agentId
  toast.visible = true

  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toast.visible = false
  }, 8000)

  loadStats()
  loadPending()
  loadRecentActivity()
}

function viewToastCase() {
  toast.visible = false
  if (toast.agentId) {
    openDetail(toast.agentId)
  }
}

function goToPending() {
  tab.value = 'pending'
  loadPending()
  document.getElementById('pending-section')?.scrollIntoView({ behavior: 'smooth' })
}

function switchTab(next) {
  tab.value = next
  if (next === 'pending') loadPending()
  if (next === 'agents') loadAgents()
  if (next === 'flagged') loadFlagged()
  if (next === 'audit') loadAuditLogs()
}

async function loadFlagged() {
  loading.value = true
  error.value = ''
  try {
    const data = await getFlaggedRegistrations()
    flaggedEntries.value = data.entries || []
    flaggedGroups.value = data.groupedByIp || []
    flaggedTotal.value = data.total || 0
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to load flagged registrations'
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    const data = await getDashboardStats()
    stats.totalAgents = data.totalAgents || 0
    stats.awaitingReview = data.awaitingReview || 0
    stats.verifiedToday = data.verifiedToday || 0
    stats.rejectedToday = data.rejectedToday || 0
    stats.pendingVerification = data.pendingVerification || 0
  } catch (err) {
    console.error('Failed to load stats', err)
  }
}

async function loadRecentActivity() {
  try {
    const data = await getRecentActivity()
    recentActivity.value = data.activity || []
  } catch (err) {
    console.error('Failed to load activity', err)
  }
}

async function loadPending() {
  loading.value = true
  error.value = ''
  try {
    const data = await getPendingCases()
    pendingCases.value = data.cases || []
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to load pending cases'
  } finally {
    loading.value = false
  }
}

async function loadAgents() {
  loading.value = true
  error.value = ''
  try {
    const data = await getAllAgents(statusFilter.value || undefined)
    agents.value = data.agents || []
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to load agents'
  } finally {
    loading.value = false
  }
}

async function loadAuditLogs() {
  loading.value = true
  error.value = ''
  try {
    const data = await getAuditLogs(auditPage.value, 20)
    auditLogs.value = data.logs || []
    auditTotal.value = data.total || 0
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to load audit logs'
  } finally {
    loading.value = false
  }
}

async function handleApprove(item) {
  error.value = ''
  try {
    await approveAgent(item.agent.agent_id, item.request.request_id)
    await Promise.all([loadPending(), loadStats(), loadRecentActivity()])
    if (tab.value === 'agents') await loadAgents()
    if (detail.value?.agent?.agent_id === item.agent.agent_id) {
      await openDetail(item.agent.agent_id)
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Approve failed'
  }
}

async function handleApproveFromDetail() {
  if (!latestRequest.value || !detail.value?.agent) return
  await handleApprove({
    agent: detail.value.agent,
    request: latestRequest.value,
  })
}

function openRejectModal(item) {
  rejectModal.open = true
  rejectModal.item = item
  rejectModal.reason = ''
}

function openRejectFromDetail() {
  if (!latestRequest.value || !detail.value?.agent) return
  openRejectModal({
    agent: detail.value.agent,
    request: latestRequest.value,
  })
}

async function confirmReject() {
  if (!rejectModal.item) return
  error.value = ''
  try {
    await rejectAgent(
      rejectModal.item.agent.agent_id,
      rejectModal.item.request.request_id,
      rejectModal.reason
    )
    rejectModal.open = false
    await Promise.all([loadPending(), loadStats(), loadRecentActivity()])
    if (tab.value === 'agents') await loadAgents()
    if (detail.value?.agent?.agent_id === rejectModal.item.agent.agent_id) {
      await openDetail(rejectModal.item.agent.agent_id)
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Reject failed'
  }
}

async function openDetail(agentID) {
  error.value = ''
  imagesLoading.value = true
  imagesError.value = ''
  documentUrl.value = ''
  documentBackUrl.value = ''
  selfieUrl.value = ''
  agentAuditLogs.value = []
  agentAuditLoading.value = true
  strikeMessage.value = ''

  try {
    detail.value = await getAgentDetail(agentID)
    try {
      const images = await getAgentImages(agentID)
      documentUrl.value = images.documentImage?.signedUrl || ''
      documentBackUrl.value = images.documentBackImage?.signedUrl || ''
      selfieUrl.value = images.selfieImage?.signedUrl || ''
      if (!documentUrl.value && !selfieUrl.value) {
        imagesError.value = 'Images could not be loaded.'
      }
    } catch (imgErr) {
      imagesError.value = imgErr.response?.data?.error || 'Images could not be loaded.'
    }

    try {
      const audit = await getAgentAuditLogs(agentID)
      agentAuditLogs.value = audit.logs || []
    } catch (auditErr) {
      if (auditErr.response?.status !== 404) {
        console.error('Failed to load agent audit logs', auditErr)
      }
      agentAuditLogs.value = []
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to load agent detail'
    detail.value = null
  } finally {
    imagesLoading.value = false
    agentAuditLoading.value = false
  }
}

function closeDetail() {
  detail.value = null
  documentUrl.value = ''
  documentBackUrl.value = ''
  selfieUrl.value = ''
  agentAuditLogs.value = []
  strikeMessage.value = ''
}

async function handleResetStrikes() {
  if (!detail.value?.agent?.agent_id) return
  resettingStrikes.value = true
  strikeMessage.value = ''
  try {
    const result = await resetAgentStrikes(detail.value.agent.agent_id)
    strikeMessage.value = result.message || 'Strikes reset successfully'
    await openDetail(detail.value.agent.agent_id)
  } catch (err) {
    strikeMessage.value = err.response?.data?.error || 'Failed to reset strikes'
  } finally {
    resettingStrikes.value = false
  }
}

function truncateFingerprint(value) {
  if (!value) return '—'
  if (value.length <= 16) return value
  return `${value.slice(0, 10)}…${value.slice(-4)}`
}

function formatGuardrail(type) {
  const labels = {
    blocked_email_domain: 'Blocked email',
    duplicate_national_id: 'Duplicate national ID',
    ip_rate_limit: 'IP rate limit',
    device_fingerprint_rate_limit: 'Device rate limit',
    verification_strike: 'Verification strike',
  }
  return labels[type] || type || 'Unknown'
}

function guardrailBadgeClass(type) {
  if (type === 'blocked_email_domain' || type === 'duplicate_national_id') return 'review'
  if (type === 'ip_rate_limit' || type === 'device_fingerprint_rate_limit') return 'rejected'
  if (type === 'verification_strike') return 'pending'
  return 'pending'
}

function changeAuditPage(delta) {
  auditPage.value = Math.max(1, auditPage.value + delta)
  loadAuditLogs()
}

function toggleAuditSort() {
  auditSortAsc.value = !auditSortAsc.value
}

async function submitExport() {
  exportModal.loading = true
  exportModal.error = ''
  try {
    const filters = {}
    if (exportModal.startDate) filters.startDate = exportModal.startDate
    if (exportModal.endDate) filters.endDate = exportModal.endDate
    if (exportModal.agentName.trim()) filters.agentName = exportModal.agentName.trim()

    const blob = await exportAuditLogs(filters)
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'audit-logs.csv'
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
    exportModal.open = false
  } catch (err) {
    exportModal.error = err.response?.data?.error || 'Export failed'
  } finally {
    exportModal.loading = false
  }
}

function num(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return 0
  return Number(value)
}

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString()
}

function formatDateOfBirth(value) {
  if (!value) return '—'
  const iso = String(value).slice(0, 10)
  const [year, month, day] = iso.split('-')
  if (year && month && day) {
    return `${day}/${month}/${year}`
  }
  return iso
}

function formatScore(value) {
  if (value === null || value === undefined) return '—'
  return Number(value).toFixed(2)
}

function formatDetails(details) {
  try {
    return JSON.stringify(details, null, 2)
  } catch {
    return String(details)
  }
}

async function handleLogout() {
  await logout()
  router.push('/login')
}
</script>

<style scoped>
.admin {
  min-height: 100vh;
  background: #f5f7fa;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 2rem;
  background: #fff;
  border-bottom: 1px solid #d9e2ec;
}

h1 {
  font-size: 1.25rem;
  color: #16213e;
}

.welcome {
  color: #627d98;
  font-size: 0.875rem;
}

.btn-logout {
  padding: 0.5rem 1rem;
  border: 1px solid #d9e2ec;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
}

.admin-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
}

.stats-bar {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  gap: 0.75rem;
  align-items: center;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.05);
  border: 1px solid #edf2f7;
}

.stat-card.clickable {
  cursor: pointer;
}

.stat-card.clickable:hover {
  border-color: #f6ad55;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  background: #edf2f7;
}

.stat-icon.amber { background: #feebc8; color: #975a16; }
.stat-icon.green { background: #c6f6d5; color: #276749; }
.stat-icon.red { background: #fed7d7; color: #9b2c2c; }
.stat-icon.grey { background: #e2e8f0; color: #4a5568; }
.stat-icon.total { background: #bee3f8; color: #2b6cb0; }

.stat-label {
  font-size: 0.75rem;
  color: #627d98;
  margin: 0;
}

.stat-value {
  font-size: 1.35rem;
  font-weight: 700;
  color: #16213e;
  margin: 0.1rem 0 0;
}

.stat-card.amber .stat-value { color: #975a16; }
.stat-card.green .stat-value { color: #276749; }
.stat-card.red .stat-value { color: #9b2c2c; }
.stat-card.grey .stat-value { color: #4a5568; }

.activity-panel {
  margin-bottom: 1rem;
}

.flagged-groups {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.ip-group {
  background: #f7fafc;
  border-radius: 8px;
  padding: 0.55rem 0.75rem;
}

.ip-group header {
  display: flex;
  gap: 0.6rem;
  align-items: center;
}

.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.8rem;
}

.activity-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  max-height: 220px;
  overflow-y: auto;
}

.activity-list li {
  display: grid;
  grid-template-columns: 1.2fr 1fr 1fr 1.4fr;
  gap: 0.5rem;
  font-size: 0.85rem;
  padding: 0.55rem 0.7rem;
  background: #f7fafc;
  border-radius: 8px;
}

.activity-time { color: #627d98; }
.activity-name { font-weight: 600; color: #243b53; }
.activity-action { color: #334e68; }
.activity-outcome { color: #486581; }

.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.tabs button {
  border: 1px solid #d9e2ec;
  background: #fff;
  border-radius: 999px;
  padding: 0.5rem 1rem;
  cursor: pointer;
}

.tabs button.active {
  background: #3e7cb1;
  border-color: #3e7cb1;
  color: #fff;
}

.panel {
  background: #fff;
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.05);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.filters {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

input, select, textarea {
  border: 1px solid #d9e2ec;
  border-radius: 8px;
  padding: 0.5rem 0.75rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin: 0.65rem 0;
  font-size: 0.875rem;
  color: #486581;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  text-align: left;
  padding: 0.75rem;
  border-bottom: 1px solid #edf2f7;
  font-size: 0.9rem;
}

th.sortable {
  cursor: pointer;
}

tr.clickable {
  cursor: pointer;
}

tr.clickable:hover {
  background: #f8fafc;
}

.linkish {
  border: none;
  background: transparent;
  color: #2b6cb0;
  cursor: pointer;
  font: inherit;
  padding: 0;
  text-decoration: underline;
}

.actions {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.btn {
  border: none;
  border-radius: 8px;
  padding: 0.4rem 0.75rem;
  cursor: pointer;
  font-weight: 600;
}

.btn.approve {
  background: #c6f6d5;
  color: #276749;
}

.btn.reject {
  background: #fed7d7;
  color: #9b2c2c;
}

.btn.ghost {
  background: #edf2f7;
  color: #2d3748;
}

.badge {
  display: inline-block;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

.badge.verified { background: #c6f6d5; color: #276749; }
.badge.review { background: #fefcbf; color: #975a16; }
.badge.rejected { background: #fed7d7; color: #9b2c2c; }
.badge.pending { background: #e2e8f0; color: #4a5568; }

.empty, .muted {
  color: #718096;
}

.error {
  color: #c53030;
  margin-bottom: 0.75rem;
}

.toast {
  position: fixed;
  top: 1.25rem;
  right: 1.25rem;
  z-index: 80;
  background: #fff;
  border: 1px solid #f6ad55;
  border-left: 4px solid #dd6b20;
  border-radius: 10px;
  padding: 0.9rem 1rem;
  display: flex;
  gap: 1rem;
  align-items: center;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.15);
  max-width: min(380px, calc(100vw - 2rem));
}

.toast-title {
  margin: 0;
  font-weight: 700;
  color: #9c4221;
  font-size: 0.9rem;
}

.toast-body {
  margin: 0.15rem 0 0;
  color: #4a5568;
  font-size: 0.85rem;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.modal-backdrop, .drawer-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 40;
}

.modal {
  background: #fff;
  border-radius: 12px;
  padding: 1.25rem;
  width: min(420px, 92vw);
}

.modal textarea {
  width: 100%;
  margin: 0.75rem 0 1rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.drawer-backdrop {
  justify-content: flex-end;
  align-items: stretch;
}

.drawer {
  width: min(520px, 96vw);
  background: #fff;
  padding: 1.25rem;
  overflow-y: auto;
}

.drawer header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.drawer-section {
  margin-bottom: 1.25rem;
}

.drawer-section h4 {
  margin: 0 0 0.65rem;
  color: #243b53;
}

.info-grid {
  display: grid;
  gap: 0.55rem;
  margin: 0;
}

.info-grid dt {
  font-size: 0.75rem;
  color: #627d98;
}

.info-grid dd {
  margin: 0.1rem 0 0;
  color: #243b53;
  font-weight: 600;
}

.image-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.img-label {
  font-size: 0.8rem;
  color: #627d98;
  margin: 0 0 0.35rem;
}

.skeleton {
  height: 180px;
  border-radius: 10px;
  background: linear-gradient(90deg, #edf2f7 25%, #f7fafc 50%, #edf2f7 75%);
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.scores {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.decision-block {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.history-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  margin: 0.5rem 0 1rem;
  padding: 0;
}

.history-list li {
  padding: 0.55rem 0.7rem;
  background: #f7fafc;
  border-radius: 8px;
  font-size: 0.85rem;
}

.audit-top {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.details-viewer {
  margin-top: 0.4rem;
}

.details-viewer summary {
  cursor: pointer;
  color: #2b6cb0;
  font-size: 0.8rem;
}

.details-viewer pre {
  margin: 0.4rem 0 0;
  padding: 0.55rem;
  background: #edf2f7;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 0.75rem;
}

.ocr-panel {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.ocr-note {
  margin: 0;
}

.ocr-grid {
  margin: 0;
}

.ocr-matches {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.match-pill {
  padding: 0.25rem 0.55rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.match-pill.ok {
  background: #c6f6d5;
  color: #276749;
}

.match-pill.bad {
  background: #fed7d7;
  color: #9b2c2c;
}

.raw-text-list {
  margin: 0.45rem 0 0;
  padding-left: 1.1rem;
  max-height: 180px;
  overflow-y: auto;
  font-size: 0.8rem;
}

@media (max-width: 1000px) {
  .stats-bar {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .activity-list li {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .stats-bar {
    grid-template-columns: 1fr;
  }

  .image-grid {
    grid-template-columns: 1fr;
  }
}
</style>
