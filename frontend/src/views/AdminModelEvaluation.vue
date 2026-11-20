<template>
  <div class="model-page workspace">
    <header class="model-header">
      <div>
        <h1>Model Evaluation</h1>
        <p class="subtitle">Saved SVM evaluation<template v-if="report?.model_version"> · v{{ report.model_version }}</template> · Synthetic test cases</p>
      </div>
      <span
        class="model-badge"
        :class="status.loading ? 'checking' : status.unknown ? 'checking' : status.modelLoaded ? 'active' : 'fallback'"
      >
        <span class="model-dot" aria-hidden="true" />
        <span v-if="status.loading">Checking live model…</span>
        <span v-else-if="status.unknown">Live status unavailable</span>
        <span v-else-if="status.modelLoaded">Live SVM<template v-if="status.modelVersion"> · v{{ status.modelVersion }}</template></span>
        <span v-else>Using threshold rules</span>
      </span>
    </header>

    <main class="model-content">
      <p v-if="loading" class="muted">Loading evaluation report…</p>
      <div v-else-if="error" class="panel error-panel">
        <p class="error">{{ error }}</p>
      </div>

      <template v-else-if="report">
        <p v-if="status.modelLoaded && status.modelVersion && report.model_version && status.modelVersion !== report.model_version" class="version-note">
          The live service reports v{{ status.modelVersion }}. These results are for v{{ report.model_version }}.
        </p>
        <section class="metric-grid" aria-label="Test set metrics">
          <article class="metric-card accuracy-card">
            <p class="metric-label">Accuracy</p>
            <p class="metric-value">{{ percent(report.accuracy) }}</p>
            <p v-if="report.correct_predictions != null" class="metric-note">{{ formatNumber(report.correct_predictions) }} of {{ formatNumber(report.split_sizes.test) }} test cases classified correctly</p>
            <p v-else class="metric-note">Share of test cases classified correctly</p>
          </article>
          <article class="metric-card">
            <p class="metric-label">Macro F1-score</p>
            <p class="metric-value">{{ f1Score(report.macro_f1) }}</p>
            <p class="metric-note">Unweighted mean F1 across the three classes</p>
          </article>
          <article class="metric-card">
            <p class="metric-label">Weighted F1-score</p>
            <p class="metric-value">{{ f1Score(report.weighted_f1) }}</p>
            <p class="metric-note">F1 weighted by class support</p>
          </article>
          <article class="metric-card">
            <p class="metric-label">Test cases</p>
            <p class="metric-value">{{ formatNumber(report.split_sizes?.test) }}</p>
            <p class="metric-note">Held out for final evaluation</p>
          </article>
          <article class="metric-card">
            <p class="metric-label">Total synthetic cases</p>
            <p class="metric-value">{{ formatNumber(report.dataset_size) }}</p>
            <p v-if="report.split_sizes" class="metric-note">
              {{ formatNumber(report.split_sizes.train) }} train ·
              {{ formatNumber(report.split_sizes.validation) }} development ·
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
              Precision measures how often a predicted class was correct. Recall measures how many cases in that class the model identified.
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
              Rows show the assigned outcomes. Columns show the model predictions. Each percentage is a share of its row.
            </p>
          </section>
        </div>

        <div v-if="report.comparisons?.length" class="two-col">
          <section class="panel">
            <h2>Version comparison</h2>
            <table class="class-table">
              <thead><tr><th scope="col">Test set</th><th scope="col">Model</th><th scope="col" class="num">Accuracy</th><th scope="col" class="num">Macro F1</th></tr></thead>
              <tbody v-for="sample in report.comparisons" :key="sample.sample">
                <tr>
                  <th scope="rowgroup" rowspan="2">{{ sample.sample }}<small class="sample-size">{{ formatNumber(sample.current.cases) }} cases</small></th>
                  <td>v{{ report.baseline_version }}</td>
                  <td class="num">{{ percent(sample.baseline.accuracy) }}</td><td class="num">{{ f1Score(sample.baseline.macro_f1) }}</td>
                </tr>
                <tr>
                  <td>v{{ report.model_version }}</td>
                  <td class="num strong">{{ percent(sample.current.accuracy) }}</td><td class="num strong">{{ f1Score(sample.current.macro_f1) }}</td>
                </tr>
              </tbody>
            </table>
            <p class="footnote">Both models saw the same cases within each test set. The headline metrics use the revised scenarios.</p>
          </section>
          <section v-if="report.face_review_probes" class="panel">
            <h2>Face matches sent to review</h2>
            <p class="probe-result">{{ report.face_review_probes['Manual Review'] }} <span>of {{ probeCount }} cases</span></p>
            <p class="probe-detail">Face similarity between 25 and 50, with perfect OCR and liveness across three held-out image-quality profiles.</p>
            <p class="footnote">v{{ report.model_version }} verified {{ report.face_review_probes.Verified }} and rejected {{ report.face_review_probes.Rejected }}. v{{ report.baseline_version }} sent {{ report.baseline_face_review_probes['Manual Review'] }} to review.</p>
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
            The simulator uses measurements from LFW, NUAA and MIDV-500. Its scenario frequencies and outcome labels are modeling assumptions. Accuracy on real applicants remains unmeasured.
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
const status = reactive({ loading: true, modelLoaded: false, modelVersion: null, unknown: false })
let statusTimer = null

const classRows = computed(() =>
  CLASS_ORDER.map((cls) => ({ ...cls, ...(report.value?.per_class?.[cls.key] || {}) }))
)

const matrixLabels = computed(() => {
  const keys = report.value?.confusion_matrix_labels
  if (!keys) return CLASS_ORDER
  return keys.map((key) => CLASS_ORDER.find((cls) => cls.key === key) || { key, label: key, short: key })
})

const probeCount = computed(() =>
  Object.values(report.value?.face_review_probes || {}).reduce((total, count) => total + count, 0)
)

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
        ? 'The saved evaluation report is unavailable.'
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
    status.unknown = data.aiServiceReachable === false || typeof data.modelLoaded !== 'boolean'
    status.modelLoaded = Boolean(data.modelLoaded)
    status.modelVersion = data.modelVersion
  } catch {
    status.unknown = true
    status.modelVersion = null
    status.modelLoaded = false
  } finally {
    status.loading = false
  }
}

// Informational intensity, independent of the verified/review/rejected labels.
// Keep the surface tint light enough for readable text in either theme.
function cellStyle(cell) {
  const t = Math.max(0, Math.min(1, cell.share))
  return {
    backgroundColor: `color-mix(in srgb, var(--info) ${Math.round(t * 20)}%, var(--surface))`,
    color: 'var(--ink)',
  }
}

function percent(value) {
  const n = value == null ? NaN : Number(value)
  if (!Number.isFinite(n)) return '—'
  return `${(n * 100).toFixed(n === 1 || n === 0 ? 0 : 2)}%`
}

function decimal(value) {
  const n = value == null ? NaN : Number(value)
  return Number.isFinite(n) ? n.toFixed(4) : '—'
}

function formatNumber(value) {
  const n = value == null ? NaN : Number(value)
  return Number.isFinite(n) ? n.toLocaleString() : '—'
}

function f1Score(value) {
  return Number.isFinite(value) ? value.toFixed(3) : '—'
}
</script>

<style scoped>
.version-note { color: var(--warning); margin: 0; }
.sample-size { display: block; font-weight: 400; color: var(--muted); }
.probe-result { font-size: 2.25rem; font-weight: 600; color: var(--ink); margin: .75rem 0; }
.probe-result span { font-size: 1rem; color: var(--muted); }
.probe-detail { line-height: 1.5; margin: 0; color: var(--ink); }
.model-page {
  min-height: 100vh;
  background: var(--surface-muted);
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
  flex-wrap: wrap;
  padding: 1.25rem 2rem;
  background: var(--surface);
  border-bottom: 1px solid var(--line);
}

.back-link {
  font-size: 0.8rem;
  color: var(--info);
  text-decoration: none;
}

h1 {
  font-size: 1.25rem;
  color: var(--ink);
  margin: 0.25rem 0 0;
}

h2 {
  font-size: 1rem;
  color: var(--ink);
  margin: 0 0 0.75rem;
}

.subtitle {
  color: var(--muted);
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

.model-badge.active { background: var(--success-bg); color: var(--success); border-color: var(--success-border); }
.model-badge.fallback { background: var(--warning-bg); color: var(--warning); border-color: var(--warning-border); }
.model-badge.checking {     background:var(--warning-bg); color:var(--warning); border-color:var(--warning-border); }

.model-content {
  container-type: inline-size;
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
  display: grid;
  gap: 1rem;
}

.metric-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.metric-card,
.panel {
  background: var(--surface);
  border-radius: 12px;
  padding: 1rem 1.25rem;
  border: 1px solid var(--surface-muted);
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.05);
}

.metric-label {
  font-size: 0.75rem;
  color: var(--muted);
  margin: 0;
}

.metric-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--ink);
  margin: 0.25rem 0;
  font-variant-numeric: tabular-nums;
}

.metric-value.small {
  font-size: 1.05rem;
  line-height: 1.6;
}

.metric-note {
  font-size: 0.75rem;
  color: var(--muted);
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
  border-bottom: 1px solid var(--surface-muted);
  text-align: left;
}

.class-table thead th {
  font-size: 0.75rem;
  color: var(--muted);
  font-weight: 600;
}

.num {
  text-align: right !important;
  font-variant-numeric: tabular-nums;
}

.strong {
  font-weight: 700;
  color: var(--ink);
}

.badge {
  display: inline-block;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
}

.badge.verified { background: var(--success-bg); color: var(--success); }
.badge.review { background: var(--warning-bg); color: var(--warning); }
.badge.rejected { background: var(--danger-bg); color: var(--danger); }

.matrix {
  display: grid;
  grid-template-columns: minmax(90px, auto) repeat(3, minmax(0, 1fr));
  gap: 2px;
}

.matrix-corner {
  display: flex;
  align-items: flex-end;
  font-size: 0.7rem;
  color: var(--muted);
  padding: 0.25rem;
}

.matrix-head {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--ink);
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
  outline-color: var(--danger);
}

.matrix-cell:hover {
  outline-color: var(--ink);
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
  color: var(--muted);
}

.meta-list dd {
  margin: 0.15rem 0 0;
  font-weight: 600;
  color: var(--ink);
  font-size: 0.875rem;
}

.footnote {
  font-size: 0.75rem;
  color: var(--muted);
  margin: 0.75rem 0 0;
  line-height: 1.5;
}

.muted {
  color: var(--muted);
}

.error {
  color: var(--danger);
  margin: 0;
}

#app .model-page .accuracy-card {
  grid-row: span 2;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: var(--sidebar-bg);
  border-color: var(--sidebar-border);
}
#app .accuracy-card .metric-label { color: var(--sidebar-text); font-size: 15px; }
#app .accuracy-card .metric-value {
  color: var(--brand-sage);
  margin-block: 12px;
  font-size: clamp(40px, 6cqi, 84px);
  font-weight: 500;
  letter-spacing: -.06em;
  line-height: 1;
}
#app .accuracy-card .metric-note { color: var(--sidebar-muted); max-width: 26ch; }
@container (max-width: 56rem) {
  .two-col { grid-template-columns: minmax(0, 1fr); }
}
@container (max-width: 38rem) {
  .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  #app .model-page .accuracy-card { grid-column: 1 / -1; grid-row: auto; }
  #app .model-page .metric-card { padding: 16px; }
  .metric-value { font-size: 24px; }
}
@container (max-width: 18rem) {
  .metric-grid { grid-template-columns: minmax(0, 1fr); }
}
</style>
