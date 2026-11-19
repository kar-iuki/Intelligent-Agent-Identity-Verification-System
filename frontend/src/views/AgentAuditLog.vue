<template>
  <div class="audit-page workspace">
    <header>
      <div>
        <h1>Activity history</h1>
        <p class="subtitle">Verification and account activity, newest first.</p>
      </div>
    </header>
    <main class="content">
      <p v-if="loading" class="history-state" role="status">Loading your activity…</p>
      <div v-else-if="error" class="history-state">
        <p role="alert">{{ error }}</p>
        <button type="button" class="btn ghost" @click="loadLogs">Try again</button>
      </div>
      <p v-else-if="!days.length" class="history-state">Your account activity will appear here.</p>
      <section v-for="day in days" :key="day.label" class="history-day">
        <h2>{{ day.label }}</h2>
        <ol>
          <li v-for="{ log, date } in day.entries" :key="log.logId">
            <time v-if="date" :datetime="date.toISOString()">{{ clock.format(date) }}</time>
            <span v-else class="unknown-time">—</span>
            <strong>{{ labelForAction(log.action) }}</strong>
            <span class="badge" :class="outcomeClass(log.outcome)">{{ log.outcome }}</span>
          </li>
        </ol>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { getMyAuditLogs } from '../services/agentService.js'
import { labelForAction } from '../utils/auditLabels.js'

const logs = ref([])
const loading = ref(true)
const error = ref('')
const calendar = new Intl.DateTimeFormat(undefined, { dateStyle: 'full' })
const clock = new Intl.DateTimeFormat(undefined, { timeStyle: 'short' })
const days = computed(() => {
  const groups = new Map()
  for (const log of logs.value) {
    const parsed = log.timestamp ? new Date(log.timestamp) : null
    const date = parsed && Number.isFinite(parsed.getTime()) ? parsed : null
    const label = date ? calendar.format(date) : 'Date unavailable'
    if (!groups.has(label)) groups.set(label, { label, entries: [] })
    groups.get(label).entries.push({ log, date })
  }
  return [...groups.values()]
})

async function loadLogs() {
  loading.value = true
  error.value = ''
  try {
    const data = await getMyAuditLogs()
    logs.value = data.logs || []
  } catch (err) {
    error.value = err.response?.data?.error || 'Could not load your activity.'
  } finally {
    loading.value = false
  }
}
onMounted(loadLogs)

function outcomeClass(outcome) {
  const value = String(outcome || '').toLowerCase()
  if (['success', 'passed', 'verified'].includes(value)) return 'ok'
  if (['pending', 'review', 'borderline'].includes(value)) return 'warn'
  if (['failed', 'rejected', 'blocked'].includes(value)) return 'bad'
  return 'neutral'
}
</script>

<style scoped>
.history-state, .history-day { max-width: 64rem; }
.history-state, .history-day ol {
  border: 1px solid var(--line);
  background: var(--surface);
  border-radius: 12px;
}
.history-state { padding: 24px; color: var(--muted); }
.history-state button { margin-top: 12px; padding-inline: 16px; }
.history-day + .history-day { margin-top: 32px; }
.history-day h2 { margin: 0 0 12px; }
.history-day ol { list-style: none; padding: 0; margin: 0; }
.history-day li {
  display: grid;
  grid-template-columns: 6rem minmax(0, 1fr) auto;
  grid-template-areas: "time event outcome";
  align-items: center;
  gap: 16px;
  padding: 18px 20px;
}
.history-day li + li { border-top: 1px solid var(--line); }
time, .unknown-time { grid-area: time; font: 12px/1.5 var(--meta-font); color: var(--muted); }
.history-day strong { grid-area: event; font-size: 14px; font-weight: 550; overflow-wrap: anywhere; }
.badge { grid-area: outcome; }
.badge.ok { background: var(--success-bg); color: var(--success); }
.badge.warn { background: var(--warning-bg); color: var(--warning); }
.badge.bad { background: var(--danger-bg); color: var(--danger); }
.badge.neutral { background: var(--surface-muted); color: var(--ink); }
@media (max-width: 600px) {
  .history-day li {
    grid-template-columns: minmax(0, 1fr) auto;
    grid-template-areas: "event outcome" "time outcome";
    gap: 4px 12px;
    padding: 16px;
  }
}
</style>
