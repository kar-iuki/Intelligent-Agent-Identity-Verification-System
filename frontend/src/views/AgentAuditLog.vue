<template>
  <div class="audit-page workspace">
    <header class="page-header">
      <div>
        <p class="workspace-eyebrow">AGENT PORTAL / AUDIT HISTORY</p>
        <h1>My audit trail</h1>
        <p class="subtitle">Read-only history of actions on your account</p>
      </div>

    </header>

    <main class="content">
      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="loading" class="muted">Loading audit trail...</p>

      <ol v-else class="timeline">
        <li v-for="log in logs" :key="log.logId" class="timeline-item">
          <div class="dot" :class="outcomeClass(log.outcome)" />
          <div class="card">
            <div class="card-top">
              <strong>{{ labelForAction(log.action) }}</strong>
              <span class="badge" :class="outcomeClass(log.outcome)">{{ log.outcome }}</span>
            </div>
            <p class="time">{{ formatDate(log.timestamp) }}</p>
          </div>
        </li>
        <li v-if="!logs.length" class="empty">No audit entries yet.</li>
      </ol>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'
import { getMyAuditLogs } from '../services/agentService.js'
import { labelForAction } from '../utils/auditLabels.js'

const router = useRouter()
const { logout } = useAuthStore()

const logs = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    const data = await getMyAuditLogs()
    logs.value = data.logs || []
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to load audit trail'
  } finally {
    loading.value = false
  }
})

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString()
}

function outcomeClass(outcome) {
  const value = String(outcome || '').toLowerCase()
  if (['success', 'passed', 'verified'].includes(value)) return 'ok'
  if (['pending', 'review', 'borderline'].includes(value)) return 'warn'
  if (['failed', 'rejected', 'blocked'].includes(value)) return 'bad'
  return 'neutral'
}

async function handleLogout() {
  await logout()
  router.push('/login')
}
</script>

<style scoped>
.audit-page {
  min-height: 100vh;
  background: var(--surface-muted);
}

.page-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding: 1.25rem 2rem;
  background: var(--surface);
  border-bottom: 1px solid var(--line);
  flex-wrap: wrap;
}

h1 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--ink);
}

.subtitle {
  margin: 0.25rem 0 0;
  color: var(--muted);
  font-size: 0.875rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.btn, .btn-logout {
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 0.5rem 0.9rem;
  background: var(--surface);
  cursor: pointer;
  text-decoration: none;
  color: var(--ink);
  font-weight: 600;
}

.content {
  max-width: 720px;
  margin: 0 auto;
  padding: 1.5rem;
}

.timeline {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.timeline-item {
  display: grid;
  grid-template-columns: 16px 1fr;
  gap: 0.85rem;
  align-items: start;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  margin-top: 0.55rem;
  background: var(--line);
}

.dot.ok { background: var(--success); }
.dot.warn { background: var(--warning); }
.dot.bad { background: var(--danger); }

.card {
  background: var(--surface);
  border-radius: 12px;
  padding: 0.9rem 1rem;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.05);
}

.card-top {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: center;
}

.time {
  margin: 0.35rem 0 0;
  color: var(--muted);
  font-size: 0.85rem;
}

.badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
}

.badge.ok { background: var(--success-bg); color: var(--success); }
.badge.warn { background: var(--warning-bg); color: var(--warning); }
.badge.bad { background: var(--danger-bg); color: var(--danger); }
.badge.neutral { background: var(--surface-muted); color: var(--ink); }

.error { color: var(--danger); }
.muted, .empty { color: var(--muted); }
</style>
