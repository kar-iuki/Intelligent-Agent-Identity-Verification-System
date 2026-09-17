<template>
  <div class="score-bar">
    <div class="meta">
      <span class="label">{{ label }}</span>
      <span class="value">{{ displayValue }}</span>
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
}

.label {
  color: #334e68;
  font-weight: 600;
}

.value {
  color: #486581;
}

.track {
  height: 10px;
  background: #edf2f7;
  border-radius: 999px;
  overflow: hidden;
}

.fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.25s ease;
}

.fill.green { background: #38a169; }
.fill.amber { background: #d69e2e; }
.fill.red { background: #e53e3e; }
</style>
