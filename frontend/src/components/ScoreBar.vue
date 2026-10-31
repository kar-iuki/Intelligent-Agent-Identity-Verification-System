<template>
  <div class="score-bar">
    <div class="meta">
      <span class="label">{{ label }}</span>
      <span class="value">{{ displayValue }} <span class="assessment" :class="tone">{{ assessment }}</span></span>
    </div>
    <div class="track">
      <div class="fill" :class="tone" :style="{ width: `${percent}%` }" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: Number, required: true },
  max: { type: Number, default: 100 },
  greenThreshold: { type: Number, required: true },
  amberThreshold: { type: Number, required: true },
  /** When true, green means value is BETWEEN amberThreshold and greenThreshold (inclusive) */
  rangeMode: { type: Boolean, default: false },
})

const percent = computed(() => {
  if (!props.max) return 0
  return Math.max(0, Math.min(100, (Number(props.value) / props.max) * 100))
})

const displayValue = computed(() => Number(props.value).toFixed(2))

const tone = computed(() => {
  const value = Number(props.value)

  if (props.rangeMode) {
    // brightness-style: green between amberThreshold (min) and greenThreshold (max)
    if (value >= props.amberThreshold && value <= props.greenThreshold) return 'green'
    return 'red'
  }

  if (value >= props.greenThreshold) return 'green'
  if (value >= props.amberThreshold) return 'amber'
  return 'red'
})

const assessment = computed(() => tone.value === 'green'
  ? 'Within range'
  : tone.value === 'amber' ? 'Needs review' : props.rangeMode ? 'Outside range' : 'Below threshold')
</script>

<style scoped>
.score-bar {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.label {
  color: var(--ink);
  font-weight: 600;
}

.value {
  color: var(--ink);
  margin-left: auto;
  text-align: right;
}

.assessment { display: inline-block; margin-left: .4rem; font-size: .7rem; }
.assessment.green { color: var(--success); }
.assessment.amber { color: var(--warning); }
.assessment.red { color: var(--danger); }

.track {
  height: 10px;
  background: var(--surface-muted);
  border-radius: 999px;
  overflow: hidden;
}

.fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.25s ease;
}

.fill.green { background: var(--success); }
.fill.amber { background: var(--warning); }
.fill.red { background: var(--danger); }
</style>
