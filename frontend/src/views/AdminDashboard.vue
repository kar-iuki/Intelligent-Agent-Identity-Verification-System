<template>
  <!-- Review starts from the agent directory and the open audit window. -->
  <div class="admin workspace">
    <header class="admin-header">
      <div>
        <h1>Verification overview</h1>
        <p class="welcome">Agent registrations, decisions, and cases awaiting review.</p>
      </div>
      <div class="header-actions">
        <router-link
          to="/admin/model"
          class="model-badge"
          :class="modelStatus.loading ? 'checking' : modelStatus.modelLoaded ? 'active' : 'fallback'"
          :title="modelStatusTitle"
        >
          <span class="model-dot" aria-hidden="true" />
          <span v-if="modelStatus.loading">Checking model…</span>
          <span v-else-if="modelStatus.modelLoaded">SVM active<template v-if="modelStatus.modelVersion"> · v{{ modelStatus.modelVersion }}</template></span>
          <span v-else>Using threshold rules</span>
        </router-link>
      </div>
    </header>

    <!-- Real-time toast -->
    <Transition name="toast">
      <div v-if="toast.visible" class="toast" role="status">
        <div>
          <p class="toast-title">New case awaiting review</p>
          <p class="toast-body">{{ toast.agentName }}</p>
        </div>
        <button class="btn approve" @click="viewToastCase">View case</button>
      </div>
    </Transition>

    <main class="admin-content">
      <p v-if="statsUnavailable" class="stats-message" role="status">Verification totals are unavailable. <button class="linkish" @click="loadStats">Retry</button></p>
      <section class="review-summary" aria-label="Verification totals">
        <button type="button" class="queue-card" @click="goToPending">
          <span class="queue-label"><Clock3 :size="18" aria-hidden="true" /> Awaiting review</span>
          <strong>{{ stats?.awaitingReview ?? '—' }}</strong>
          <span class="queue-action">Open review queue <ArrowRight :size="18" aria-hidden="true" /></span>
        </button>

        <article class="outcomes-card">
          <h2>Today’s outcomes</h2>
          <p>For requests submitted today</p>
          <dl class="outcome-counts">
            <div><dt><span class="stat-icon green" aria-hidden="true"></span>Verified</dt><dd>{{ stats?.verifiedToday ?? '—' }}</dd></div>
            <div><dt><span class="stat-icon red" aria-hidden="true"></span>Rejected</dt><dd>{{ stats?.rejectedToday ?? '—' }}</dd></div>
          </dl>
          <div class="outcome-bar" aria-hidden="true">
            <template v-if="stats && stats.verifiedToday != null && stats.rejectedToday != null">
              <span class="verified-share" :style="{ flexGrow: stats.verifiedToday }"></span>
              <span class="rejected-share" :style="{ flexGrow: stats.rejectedToday }"></span>
            </template>
          </div>
        </article>

        <dl class="registration-totals">
          <div><dt><Users :size="16" aria-hidden="true" />Total agents</dt><dd>{{ stats?.totalAgents ?? '—' }}</dd></div>
          <div><dt><ScanFace class="stat-icon grey" :size="16" aria-hidden="true" />Pending verification</dt><dd>{{ stats?.pendingVerification ?? '—' }}</dd></div>
        </dl>
      </section>

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
      <section v-if="tab === 'agents' || tab === 'recent'" class="panel">
        <div class="toolbar">
          <div><h2>{{ tab === 'recent' ? 'Verified · open audit window' : 'Agent directory' }}</h2>
            <p v-if="tab === 'recent'" class="muted">Verified files are kept for 3 business days after the decision. Weekends are excluded.</p></div>
          <div class="filters">
            <input v-model="search" aria-label="Search agents" type="search" placeholder="Search name or national ID" />
            <select v-if="tab !== 'recent'" aria-label="Filter agents by status" v-model="statusFilter" @change="loadAgents">
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
                <th>{{ tab === 'recent' ? 'Verified at' : 'Submission date' }}</th>
                <th>Audit deadline</th>
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
                <td><span class="badge" :class="item.status">{{ reviewLabel(item.request) || item.status }}</span></td>
                <td>{{ formatDate(tab === 'recent' ? item.auditWindow?.verifiedAt : item.request?.created_at || item.agent.created_at) }}</td>
                <td><span v-if="item.auditWindow?.expiresAt" :class="{ muted: !item.auditWindow.open }">{{ formatDate(item.auditWindow.expiresAt) }}<small class="audit-state">{{ item.auditWindow.open ? 'Available for review' : 'Retention period ended' }}</small></span><span v-else class="muted">—</span></td>
                <td><button class="btn ghost" @click.stop="openDetail(item.agent.agent_id)">View</button></td>
              </tr>
              <tr v-if="!filteredAgents.length && !loading">
                <td colspan="6" class="empty">{{ tab === 'recent' ? 'No verified agents with an open audit window.' : 'No agents found.' }}</td>
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
              <span class="badge rejected">{{ group.count }} blocked attempt{{ group.count === 1 ? '' : 's' }}</span>
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
                <th :aria-sort="auditSortAsc ? 'ascending' : 'descending'"><button type="button" class="sort-time" @click="toggleAuditSort">Timestamp <span aria-hidden="true">{{ auditSortAsc ? '↑' : '↓' }}</span></button></th>
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
      <aside class="drawer" aria-labelledby="record-title">
        <header>
          <h3 id="record-title">{{ detail.agent.full_name || 'Agent detail' }}</h3>
          <button class="btn ghost" @click="closeDetail">Close</button>
        </header>

        <section class="drawer-section">
          <h4>Agent information</h4>
          <dl class="info-grid">
            <div><dt>Email</dt><dd>{{ detail.agent.email || '—' }}</dd></div>
            <div><dt>Phone</dt><dd>{{ detail.agent.phone_number || '—' }}</dd></div>
            <div><dt>National ID</dt><dd>{{ detail.agent.national_id }}</dd></div>
            <div><dt>Date of birth</dt><dd>{{ formatDateOfBirth(detail.agent.date_of_birth) }}</dd></div>
            <div><dt>Registered</dt><dd>{{ formatDate(detail.agent.created_at) }}</dd></div>
          </dl>
        </section>

        <section class="drawer-section">
          <h4>Document images</h4>
          <p v-if="detail.history?.[0]?.auditWindow?.expiresAt" class="muted">Case deadline: {{ formatDate(detail.history[0].auditWindow.expiresAt) }}. {{ detail.history[0].auditWindow.open ? 'Pending and verified files have a 3-business-day window. Review and rejected files have 5 business days.' : 'Retention period ended; files are scheduled for automatic deletion.' }}</p>
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
                :start-index="documentUrl ? 1 : 0"
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
                <dt>Document type</dt>
                <dd>{{ latestOcr.documentType || '—' }}</dd>
              </div>
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
            <p v-if="latestOcr.needsManualReview" class="muted ocr-note">
              Flagged for manual review{{ latestOcr.rejectReason ? `: ${latestOcr.rejectReason}` : '.' }}
            </p>
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
              v-bind="verificationScoreScales.faceMatchScore"
            />
            <ScoreBar
              label="Liveness"
              :value="num(latestScores.liveness_score)"
              v-bind="verificationScoreScales.livenessScore"
            />
            <ScoreBar
              label="OCR confidence"
              :value="num(latestScores.ocr_confidence_score)"
              v-bind="verificationScoreScales.ocrConfidenceScore"
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
            <span class="badge" :class="latestRequest.status">{{ reviewLabel(latestRequest) || latestRequest.status }}</span>
            <p v-if="latestRequest.admin_reviewed_at" class="muted">Reviewed {{ formatDate(latestRequest.admin_reviewed_at) }}</p>
            <p v-if="latestDecision?.decided_at" class="muted">
              Automated result: {{ decisionLabel(latestDecision.final_decision) }} · {{ formatDate(latestDecision.decided_at) }}
            </p>
            <p
              v-if="latestDecision"
              class="basis-label"
              :class="decisionBasisInfo(latestDecision.decision_basis).tone"
            >
              {{ decisionBasisInfo(latestDecision.decision_basis).label }}
            </p>
            <p v-if="latestDecision?.decision_basis === 'svm_model'" class="muted probabilities">
              P(verified) {{ formatProbability(latestDecision.verified_probability) }} ·
              P(review) {{ formatProbability(latestDecision.review_probability) }} ·
              P(rejected) {{ formatProbability(latestDecision.rejected_probability) }}
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
            <div v-if="previousDecisions.length" class="previous-decisions">
              <p class="muted">Previous decisions</p>
              <ul>
                <li v-for="item in previousDecisions" :key="item.decision.decision_id">
                  <span class="badge" :class="item.request.status">{{ reviewLabel(item.request) || item.request.status }}</span>
                  <span v-if="item.decision.final_decision" class="muted">Automated result: {{ decisionLabel(item.decision.final_decision) }} · {{ formatDate(item.decision.decided_at) }}</span>
                  <span class="basis-label" :class="decisionBasisInfo(item.decision.decision_basis).tone">
                    {{ decisionBasisInfo(item.decision.decision_basis).label }}
                  </span>
                </li>
              </ul>
            </div>
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
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { ArrowRight, Users, Clock3, ScanFace } from '@lucide/vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'
import Lightbox from '../components/Lightbox.vue'
import { verificationScoreScales } from '../utils/verificationScoreScales.js'
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
  getModelStatus,
} from '../services/adminService.js'
import { connectAdminSocket, disconnectAdminSocket } from '../services/socket.js'

const router = useRouter()
const route = useRoute()
const validViews = ['agents', 'pending', 'recent', 'flagged', 'audit']
const routeView = () => validViews.includes(route.query.view) ? route.query.view : 'agents'
const { logout } = useAuthStore()

const tab = ref(routeView())
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

const stats = ref(null)
const statsUnavailable = ref(false)

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
const previousDecisions = computed(() =>
  (detail.value?.history || []).slice(1).filter((item) => item.decision)
)

const MODEL_STATUS_REFRESH_MS = 60000
const modelStatus = reactive({
  loading: true,
  modelLoaded: false,
  modelVersion: null,
  trainedAt: null,
  aiServiceReachable: true,
})
const modelStatusTitle = computed(() => {
  if (modelStatus.loading) return 'Checking SVM model status'
  if (modelStatus.modelLoaded) return 'KYC decisions are made by the SVM classifier. Click for evaluation metrics.'
  return modelStatus.aiServiceReachable
    ? 'The AI service is running but the SVM model is not loaded; decisions use threshold rules.'
    : 'The AI service is unreachable; decisions use threshold rules.'
})
let modelStatusTimer = null

const DECISION_BASIS = {
  legacy_admin_override: { label: 'Original automated prediction unavailable', tone: 'neutral' },
  svm_model: { label: 'SVM prediction', tone: 'svm' },
  placeholder_threshold: { label: 'Decision made by threshold rules', tone: 'threshold' },
  image_quality_failure: { label: 'Rejected at image quality check', tone: 'neutral' },
}

function reviewLabel(request) {
  if (!request?.admin_reviewed_at) return null
  return request.status === 'verified' ? 'Approved by admin' : 'Rejected by admin'
}

function decisionLabel(value) {
  return { verified: 'Verified', review: 'Manual Review', rejected: 'Rejected' }[value]
}

function decisionBasisInfo(basis) {
  return DECISION_BASIS[basis || 'placeholder_threshold'] || { label: `Decision basis: ${basis}`, tone: 'neutral' }
}

function formatProbability(value) {
  const n = Number(value)
  return Number.isFinite(n) ? `${(n * 100).toFixed(1)}%` : '—'
}

async function loadModelStatus() {
  try {
    const data = await getModelStatus()
    modelStatus.modelLoaded = Boolean(data.modelLoaded)
    modelStatus.modelVersion = data.modelVersion
    modelStatus.trainedAt = data.trainedAt
    modelStatus.aiServiceReachable = data.aiServiceReachable !== false
  } catch (err) {
    console.error('Failed to load model status', err)
    modelStatus.modelLoaded = false
  } finally {
    modelStatus.loading = false
  }
}

const lightboxImages = computed(() => {
  const images = []
  if (documentUrl.value) images.push({ url: documentUrl.value, alt: 'Identity document' })
  if (documentBackUrl.value) images.push({ url: documentBackUrl.value, alt: 'ID back' })
  if (selfieUrl.value) images.push({ url: selfieUrl.value, alt: 'Selfie' })
  return images
})

onMounted(async () => {
  switchTab(routeView())
  await Promise.all([loadStats(), loadRecentActivity()])
  activityTimer = setInterval(() => {
    loadRecentActivity()
    loadStats()
    if (tab.value === 'recent') loadAgents()
  }, 30000)
  loadModelStatus()
  modelStatusTimer = setInterval(loadModelStatus, MODEL_STATUS_REFRESH_MS)

  socket = connectAdminSocket()
  socket.on('new_review_case', onNewReviewCase)
})

onBeforeUnmount(() => {
  if (activityTimer) clearInterval(activityTimer)
  if (modelStatusTimer) clearInterval(modelStatusTimer)
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

async function goToPending() {
  if (tab.value !== 'pending') switchTab('pending')
  await nextTick()
  document.getElementById('pending-section')?.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' })
}

watch(() => route.query.view, () => switchTab(routeView()))

function switchTab(next) {
  tab.value = next
  if (routeView() !== next) router.replace({ query: { ...route.query, view: next } })
  if (next === 'pending') loadPending()
  if (next === 'agents' || next === 'recent') {
    agents.value = []
    loadAgents()
  }
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
    stats.value = data
    statsUnavailable.value = false
  } catch {
    stats.value = null
    statsUnavailable.value = true
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
    const requestedTab = tab.value
    const data = await getAllAgents(requestedTab === 'recent' ? 'verified' : statusFilter.value || undefined, requestedTab === 'recent')
    if (tab.value === requestedTab) agents.value = data.agents || []
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
    if (['agents', 'recent'].includes(tab.value)) await loadAgents()
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
    if (['agents', 'recent'].includes(tab.value)) await loadAgents()
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

function guardrailBadgeClass() {
  // This table lists blocked registration attempts.
  return 'rejected'
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
  background: var(--surface-muted);
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 2rem;
  background: var(--surface);
  border-bottom: 1px solid var(--line);
}

h1 {
  font-size: 1.25rem;
  color: var(--ink);
}

.welcome {
  color: var(--muted);
  font-size: 0.875rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.model-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  text-decoration: none;
  border: 1px solid transparent;
  white-space: nowrap;
}

.model-badge .model-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.model-badge.active { background: var(--success-bg); color: var(--success); border-color: var(--success-border); }
.model-badge.fallback { background: var(--warning-bg); color: var(--warning); border-color: var(--warning-border); }
.model-badge.checking {     background:var(--warning-bg); color:var(--warning); border-color:var(--warning-border); }

.basis-label {
  display: inline-block;
  margin: 0.35rem 0 0;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  font-size: 0.78rem;
  font-weight: 600;
}

.basis-label.svm { background: var(--info-bg); color: var(--info); }
.basis-label.threshold { background: var(--warning-bg); color: var(--warning); }
.basis-label.neutral { background: var(--surface-muted); color: var(--ink); }

.probabilities {
  font-size: 0.8rem;
  margin-top: 0.25rem;
}

.previous-decisions {
  margin-top: 0.75rem;
  border-top: 1px solid var(--surface-muted);
  padding-top: 0.5rem;
}

.previous-decisions ul {
  list-style: none;
  padding: 0;
  margin: 0.25rem 0 0;
  display: grid;
  gap: 0.4rem;
}

.previous-decisions li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  font-size: 0.8rem;
}

.previous-decisions .basis-label {
  margin: 0;
}

.btn-logout {
  padding: 0.5rem 1rem;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface);
  cursor: pointer;
}

.admin-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
}

.stats-message { margin-bottom:12px; color:var(--muted); font-size:14px; }
.admin-content { container-type:inline-size; }
.review-summary { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1.3fr) minmax(0,.85fr); gap:16px; margin-bottom:24px; }
.review-summary > * { min-width:0; margin:0; border-radius:12px; border:1px solid var(--line); background:var(--surface); }
.queue-card { display:flex; flex-direction:column; align-items:stretch; padding:20px 24px; color:#f3f6ed; text-align:left; background:#17231c; border-color:#314537; }
.queue-card:hover { background:#223629; }
.queue-label,.queue-action,.registration-totals dt,.outcome-counts dt { display:flex; align-items:center; gap:8px; }
.queue-label,.registration-totals dt,.outcome-counts dt { font-size:14px; }
.queue-label { color:#d4dfd4; }
.queue-card strong { font-size:clamp(40px,4.5vw,68px); line-height:1.1; font-weight:500; letter-spacing:-.045em; padding:8px 0 16px; }
.queue-action { margin-top:auto; padding-top:12px; border-top:1px solid #435146; color:var(--brand-sage); font-size:14px; justify-content:space-between; }
.outcomes-card { padding:20px 24px; display:flex; flex-direction:column; }
.outcomes-card > p { font-size:13px; color:var(--muted); }
.outcome-counts { display:grid; grid-template-columns:1fr 1fr; gap:16px; margin:16px 0 12px; }
.outcome-counts dt,.registration-totals dt { color:var(--muted); }
.outcome-counts dd,.registration-totals dd { font-size:28px; line-height:1.2; font-weight:500; margin:4px 0 0; }
.review-summary :is(dd,strong) { font-variant-numeric:tabular-nums; overflow-wrap:anywhere; }
.outcome-counts .stat-icon { display:inline-block; width:8px; height:8px; border-radius:2px; background:currentColor; }
.stat-icon.green { color:var(--success); }
.stat-icon.red { color:var(--danger); }
.stat-icon.grey { color:var(--warning); }
.outcome-bar { margin-top:auto; display:flex; height:8px; background:var(--surface-muted); border-radius:4px; overflow:hidden; }
.outcome-bar span { flex-basis:0; }
.verified-share { background:var(--success); }
.rejected-share { background:var(--danger); }
.registration-totals { display:grid; padding:0 20px; }
.registration-totals > div { display:flex; flex-direction:column; justify-content:center; padding:12px 0; }
.registration-totals > div + div { border-top:1px solid var(--line); }
.registration-totals svg { flex:none; }
@container (max-width:820px) {
  .review-summary { grid-template-columns:minmax(0,1fr) minmax(0,1.25fr); gap:12px; }
  .registration-totals { grid-column:1 / -1; grid-template-columns:1fr 1fr; padding:12px 16px; }
  .registration-totals > div { padding:0; }
  .registration-totals > div + div { border-top:0; border-left:1px solid var(--line); padding-left:16px; }
}
@container (max-width:520px) {
  .review-summary { grid-template-columns:minmax(0,1fr); }
  .queue-card { display:grid; grid-template-columns:1fr auto; gap:12px; align-items:center; padding:16px 20px; }
  .queue-card strong { padding:0; font-size:40px; }
  .queue-action { grid-column:1 / -1; }
  .outcomes-card { padding:16px 20px; }
}
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
  background: var(--surface-muted);
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
  background: var(--surface-muted);
  border-radius: 8px;
}

.activity-time { color: var(--muted); }
.activity-name { font-weight: 600; color: var(--ink); }
.activity-action { color: var(--ink); }
.activity-outcome { color: var(--ink); }

.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.tabs button {
  border: 1px solid var(--line);
  background: var(--surface);
  border-radius: 999px;
  padding: 0.5rem 1rem;
  cursor: pointer;
}

.tabs button.active {
  background: var(--action);
  border-color: var(--action);
  color: var(--on-brand);
}

.panel {
  background: var(--surface);
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
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 0.5rem 0.75rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin: 0.65rem 0;
  font-size: 0.875rem;
  color: var(--ink);
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
  border-bottom: 1px solid var(--surface-muted);
  font-size: 0.9rem;
}

.sort-time {
  border:0;
  background:transparent;
  color:inherit;
  font:inherit;
  text-transform:inherit;
  cursor: pointer;
}

tr.clickable {
  cursor: pointer;
}

tr.clickable:hover {
  background: var(--surface-muted);
}

.linkish {
  border: none;
  background: transparent;
  color: var(--info);
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

.btn.reject {
  background: var(--danger-bg);
  color: var(--danger);
}

.btn.ghost {
  background: var(--surface-muted);
  color: var(--ink);
}

.badge {
  display: inline-block;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: capitalize;
}

.badge.verified { background: var(--success-bg); color: var(--success); }
.badge.review { background: var(--warning-bg); color: var(--warning); }
.badge.rejected { background: var(--danger-bg); color: var(--danger); }
.badge.pending {    background:var(--warning-bg); color:var(--warning); border-color:var(--warning-border); }

.empty, .muted {
  color: var(--muted);
}

.error {
  color: var(--danger);
  margin-bottom: 0.75rem;
}

.toast {
  position: fixed;
  top: 1.25rem;
  right: 1.25rem;
  z-index: 80;
  background: var(--surface);
  border: 1px solid var(--warning-border);
  border-left: 4px solid var(--warning-border);
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
  color: var(--warning);
  font-size: 0.9rem;
}

.toast-body {
  margin: 0.15rem 0 0;
  color: var(--ink);
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
  z-index: 72;
}

.modal-backdrop { z-index: 73; }

.modal {
  background: var(--surface);
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
  width: min(576px, 100%);
  background: var(--surface);
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
  color: var(--ink);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 13rem), 1fr));
  gap: 16px 24px;
  overflow-wrap: anywhere;
  margin: 0;
}

.info-grid dt {
  font-size: 0.75rem;
  color: var(--muted);
}

.info-grid dd {
  margin: 0.1rem 0 0;
  color: var(--ink);
  font-weight: 600;
}

.image-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.img-label {
  font-size: 0.8rem;
  color: var(--muted);
  margin: 0 0 0.35rem;
}

.skeleton {
  height: 180px;
  border-radius: 10px;
  background: var(--surface-muted);
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
  background: var(--surface-muted);
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
  color: var(--info);
  font-size: 0.8rem;
}

.details-viewer pre {
  margin: 0.4rem 0 0;
  padding: 0.55rem;
  background: var(--surface-muted);
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
  background: var(--success-bg);
  color: var(--success);
}

.match-pill.bad {
  background: var(--danger-bg);
  color: var(--danger);
}

.raw-text-list {
  margin: 0.45rem 0 0;
  padding-left: 1.1rem;
  max-height: 180px;
  overflow-y: auto;
  font-size: 0.8rem;
}

@media (max-width: 1000px) {
  .activity-list li {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .image-grid {
    grid-template-columns: 1fr;
  }
}
</style>
