<template>
  <div class="audit-page">
    <header class="page-header">
      <div>
        <h1>My audit trail</h1>
        <p class="subtitle">Read-only history of actions on your account</p>
      </div>
      <div class="header-actions">
        <router-link class="btn ghost" to="/agent/dashboard">Back to dashboard</router-link>
        <button class="btn-logout" @click="handleLogout">Sign Out</button>
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
  if (['review', 'borderline'].includes(value)) return 'warn'
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
  background: #f5f7fa;
}

.page-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding: 1.25rem 2rem;
  background: #fff;
  border-bottom: 1px solid #d9e2ec;
  flex-wrap: wrap;
}

h1 {
  margin: 0;
  font-size: 1.25rem;
  color: #16213e;
}

.subtitle {
  margin: 0.25rem 0 0;
  color: #627d98;
  font-size: 0.875rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.btn, .btn-logout {
  border: 1px solid #d9e2ec;
  border-radius: 8px;
  padding: 0.5rem 0.9rem;
  background: #fff;
  cursor: pointer;
  text-decoration: none;
  color: #2d3748;
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
  background: #cbd5e0;
}

.dot.ok { background: #38a169; }
.dot.warn { background: #d69e2e; }
.dot.bad { background: #e53e3e; }

.card {
  background: #fff;
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
  color: #718096;
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

.badge.ok { background: #c6f6d5; color: #276749; }
.badge.warn { background: #fefcbf; color: #975a16; }
.badge.bad { background: #fed7d7; color: #9b2c2c; }
.badge.neutral { background: #e2e8f0; color: #4a5568; }

.error { color: #c53030; }
.muted, .empty { color: #718096; }
</style>
