<template>
  <div class="model-page workspace">
    <header class="model-header">
      <div>
        <router-link to="/admin/dashboard" class="back-link">← Admin Dashboard</router-link>
        <p class="workspace-eyebrow">INTELLIGENCE / MODEL PERFORMANCE</p>
        <h1>Model Evaluation</h1>
        <p class="subtitle">SVM KYC classifier — held-out test set performance</p>
      </div>
      <span
        class="model-badge"
        :class="status.loading ? 'checking' : status.modelLoaded ? 'active' : 'fallback'"
      >
        <span class="model-dot" aria-hidden="true" />
        <span v-if="status.loading">Checking model…</span>
        <span v-else-if="status.modelLoaded">SVM Model Active v{{ status.modelVersion }}</span>
        <span v-else>Fallback Mode — Threshold Rules</span>
      </span>
    </header>

    <main class="model-content">
      <p v-if="loading" class="muted">Loading evaluation report…</p>
      <div v-else-if="error" class="panel error-panel">
        <p class="error">{{ error }}</p>
      </div>

      <template v-else-if="report">
        <section class="metric-grid">
          <article class="metric-card">
            <p class="metric-label">Accuracy</p>
            <p class="metric-value">{{ percent(report.accuracy) }}</p>
            <p class="metric-note">Share of test records classified correctly</p>
          </article>
          <article class="metric-card">
            <p class="metric-label">Macro F1-score</p>
            <p class="metric-value">{{ percent(report.macro_f1) }}</p>
            <p class="metric-note">Unweighted mean F1 across the three classes</p>
          </article>
          <article class="metric-card">
            <p class="metric-label">Weighted F1-score</p>
            <p class="metric-value">{{ percent(report.weighted_f1) }}</p>
            <p class="metric-note">F1 weighted by class support</p>
          </article>
          <article class="metric-card">
            <p class="metric-label">Training date</p>
            <p class="metric-value small">{{ formatDate(report.training_date) }}</p>
            <p class="metric-note">Model version {{ report.model_version || '—' }}</p>
          </article>
          <article class="metric-card">
            <p class="metric-label">Dataset size</p>
            <p class="metric-value">{{ formatNumber(report.dataset_size) }}</p>
            <p v-if="report.split_sizes" class="metric-note">
              {{ formatNumber(report.split_sizes.train) }} train ·
              {{ formatNumber(report.split_sizes.validation) }} validation ·
              {{ formatNumber(report.split_sizes.test) }} test
            </p>
          </article>
        </section>

        <div class="two-col">
          <section class="panel">
            <h2>Per-class performance</h2>
            <table class="class-table">
              <thead>
                <tr>
                  <th scope="col">Class</th>
                  <th scope="col" class="num">Precision</th>
                  <th scope="col" class="num">Recall</th>
                  <th scope="col" class="num">F1-score</th>
                  <th scope="col" class="num">Support</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in classRows" :key="row.key">
                  <th scope="row">
                    <span class="badge" :class="row.key">{{ row.label }}</span>
                  </th>
                  <td class="num">{{ decimal(row.precision) }}</td>
                  <td class="num">{{ decimal(row.recall) }}</td>
                  <td class="num strong">{{ decimal(row.f1) }}</td>
                  <td class="num muted">{{ formatNumber(row.support) }}</td>
                </tr>
              </tbody>
            </table>
            <p class="footnote">
              Precision: of the agents the model put in a class, how many belonged there.
              Recall: of the agents in a class, how many the model found.
            </p>
          </section>

          <section class="panel">
            <h2>Confusion matrix</h2>
            <div class="matrix" role="table" aria-label="Confusion matrix: rows are actual class, columns are predicted class">
              <div class="matrix-corner" role="columnheader">
                <span>Actual ↓ / Predicted →</span>
              </div>
              <div
                v-for="label in matrixLabels"
                :key="`col-${label.key}`"
                class="matrix-head"
                role="columnheader"
              >
                {{ label.short }}
              </div>

              <template v-for="(row, i) in matrixRows" :key="`row-${i}`">
                <div class="matrix-head row-head" role="rowheader">{{ matrixLabels[i].short }}</div>
                <div
                  v-for="(cell, j) in row"
                  :key="`cell-${i}-${j}`"
                  class="matrix-cell"
                  :class="{ diagonal: i === j, error: i !== j && cell.count > 0 }"
                  :style="cellStyle(cell)"
                  role="cell"
                  :title="`Actual ${matrixLabels[i].label}, predicted ${matrixLabels[j].label}: ${cell.count} (${percent(cell.share)} of actual ${matrixLabels[i].label})`"
                >
                  <span class="cell-count">{{ formatNumber(cell.count) }}</span>
                  <span class="cell-share">{{ percent(cell.share) }}</span>
                </div>
              </template>
            </div>
            <p class="footnote">
              Shading shows each cell's share of its actual class. Diagonal cells are correct
              decisions; off-diagonal cells with errors are outlined in red. The most costly error is a
              Rejected agent predicted as Verified (bottom-left).
            </p>
          </section>
        </div>

        <section v-if="report.best_params" class="panel meta-panel">
          <h2>Model configuration</h2>
          <dl class="meta-list">
            <div>
              <dt>Kernel</dt>
              <dd>{{ report.kernel || 'rbf' }}</dd>
            </div>
            <div>
              <dt>C</dt>
              <dd>{{ report.best_params.C }}</dd>
            </div>
            <div>
              <dt>gamma</dt>
              <dd>{{ report.best_params.gamma }}</dd>
            </div>
            <div v-if="report.features">
              <dt>Features</dt>
              <dd>{{ report.features.join(', ') }}</dd>
            </div>
          </dl>
          <p class="footnote">
            Metrics are measured on the held-out test split of the synthetic training dataset,
            informed by local LFW, NUAA and MIDV-500 measurements. Scenario frequencies and
            adjudication outcomes are modelling assumptions. These metrics and probabilities
            do not establish real-world performance or fraud prevalence.
          </p>
        </section>
      </template>
    </main>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { getModelEvaluation, getModelStatus } from '../services/adminService.js'

const CLASS_ORDER = [
  { key: 'verified', label: 'Verified', short: 'Verified' },
  { key: 'review', label: 'Manual Review', short: 'Review' },
  { key: 'rejected', label: 'Rejected', short: 'Rejected' },
]

const report = ref(null)
const loading = ref(true)
const error = ref('')
const status = reactive({ loading: true, modelLoaded: false, modelVersion: null })
let statusTimer = null

const classRows = computed(() =>
  CLASS_ORDER.map((cls) => ({ ...cls, ...(report.value?.per_class?.[cls.key] || {}) }))
)

const matrixLabels = computed(() => {
  const keys = report.value?.confusion_matrix_labels
  if (!keys) return CLASS_ORDER
  return keys.map((key) => CLASS_ORDER.find((cls) => cls.key === key) || { key, label: key, short: key })
})

const matrixRows = computed(() =>
  (report.value?.confusion_matrix || []).map((row) => {
    const total = row.reduce((sum, value) => sum + value, 0)
    return row.map((count) => ({ count, share: total ? count / total : 0 }))
  })
)

onMounted(async () => {
  loadStatus()
  statusTimer = setInterval(loadStatus, 60000)
  try {
    report.value = await getModelEvaluation()
  } catch (err) {
    error.value =
      err.response?.status === 404
        ? 'No evaluation report found. Train the model with `python ml/train_model.py` in the ai-service folder.'
        : err.response?.data?.error || 'Failed to load the evaluation report.'
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  if (statusTimer) clearInterval(statusTimer)
})

async function loadStatus() {
  try {
    const data = await getModelStatus()
    status.modelLoaded = Boolean(data.modelLoaded)
    status.modelVersion = data.modelVersion
  } catch {
    status.modelLoaded = false
  } finally {
    status.loading = false
  }
}

// Single-hue sequential ramp (light → dark blue) by share of the actual class
const RAMP_LOW = [235, 248, 255]
const RAMP_HIGH = [43, 108, 176]

function cellStyle(cell) {
  const t = Math.max(0, Math.min(1, cell.share))
  const rgb = RAMP_LOW.map((low, i) => Math.round(low + (RAMP_HIGH[i] - low) * t))
  return {
    backgroundColor: `rgb(${rgb.join(', ')})`,
    color: t > 0.55 ? '#ffffff' : '#16213e',
  }
}

function percent(value) {
  const n = Number(value)
  if (!Number.isFinite(n)) return '—'
  return `${(n * 100).toFixed(n === 1 || n === 0 ? 0 : 2)}%`
}

function decimal(value) {
  const n = Number(value)
  return Number.isFinite(n) ? n.toFixed(4) : '—'
}

function formatNumber(value) {
  const n = Number(value)
  return Number.isFinite(n) ? n.toLocaleString() : '—'
}

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
}
</script>

<style scoped>
.model-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
  flex-wrap: wrap;
  padding: 1.25rem 2rem;
  background: #fff;
  border-bottom: 1px solid #d9e2ec;
}

.back-link {
  font-size: 0.8rem;
  color: #2b6cb0;
  text-decoration: none;
}

h1 {
  font-size: 1.25rem;
  color: #16213e;
  margin: 0.25rem 0 0;
}

h2 {
  font-size: 1rem;
  color: #16213e;
  margin: 0 0 0.75rem;
}

.subtitle {
  color: #627d98;
  font-size: 0.875rem;
  margin: 0.15rem 0 0;
}

.model-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  border: 1px solid transparent;
}

.model-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.model-badge.active { background: #c6f6d5; color: #276749; border-color: #9ae6b4; }
.model-badge.fallback { background: #feebc8; color: #975a16; border-color: #fbd38d; }
.model-badge.checking { background: #edf2f7; color: #4a5568; border-color: #e2e8f0; }

.model-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
  display: grid;
  gap: 1rem;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 0.75rem;
}

.metric-card,
.panel {
  background: #fff;
  border-radius: 12px;
  padding: 1rem 1.25rem;
  border: 1px solid #edf2f7;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.05);
}

.metric-label {
  font-size: 0.75rem;
  color: #627d98;
  margin: 0;
}

.metric-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #16213e;
  margin: 0.25rem 0;
  font-variant-numeric: tabular-nums;
}

.metric-value.small {
  font-size: 1.05rem;
  line-height: 1.6;
}

.metric-note {
  font-size: 0.75rem;
  color: #718096;
  margin: 0;
}

.two-col {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr);
  gap: 1rem;
}

.class-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.class-table th,
.class-table td {
  padding: 0.6rem 0.5rem;
  border-bottom: 1px solid #edf2f7;
  text-align: left;
}

.class-table thead th {
  font-size: 0.75rem;
  color: #627d98;
  font-weight: 600;
}

.num {
  text-align: right !important;
  font-variant-numeric: tabular-nums;
}

.strong {
  font-weight: 700;
  color: #16213e;
}

.badge {
  display: inline-block;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
}

.badge.verified { background: #c6f6d5; color: #276749; }
.badge.review { background: #fefcbf; color: #975a16; }
.badge.rejected { background: #fed7d7; color: #9b2c2c; }

.matrix {
  display: grid;
  grid-template-columns: minmax(90px, auto) repeat(3, minmax(0, 1fr));
  gap: 2px;
}

.matrix-corner {
  display: flex;
  align-items: flex-end;
  font-size: 0.7rem;
  color: #718096;
  padding: 0.25rem;
}

.matrix-head {
  font-size: 0.8rem;
  font-weight: 600;
  color: #4a5568;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem;
}

.matrix-head.row-head {
  justify-content: flex-start;
}

.matrix-cell {
  border-radius: 6px;
  min-height: 72px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.1rem;
  font-variant-numeric: tabular-nums;
  cursor: default;
  outline: 2px solid transparent;
  outline-offset: -2px;
}

.matrix-cell.error {
  outline-color: #e53e3e;
}

.matrix-cell:hover {
  outline-color: #16213e;
}

.cell-count {
  font-size: 1.2rem;
  font-weight: 700;
}

.cell-share {
  font-size: 0.72rem;
  opacity: 0.85;
}

.meta-list {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  margin: 0;
}

.meta-list dt {
  font-size: 0.75rem;
  color: #627d98;
}

.meta-list dd {
  margin: 0.15rem 0 0;
  font-weight: 600;
  color: #16213e;
  font-size: 0.875rem;
}

.footnote {
  font-size: 0.75rem;
  color: #718096;
  margin: 0.75rem 0 0;
  line-height: 1.5;
}

.muted {
  color: #718096;
}

.error {
  color: #c53030;
  margin: 0;
}

@media (max-width: 1000px) {
  .metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .two-col {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .model-header {
    padding: 1rem;
  }

  .model-content {
    padding: 1rem;
  }

  .metric-grid {
    grid-template-columns: 1fr;
  }

  .class-table {
    font-size: 0.8rem;
  }
}
</style>
