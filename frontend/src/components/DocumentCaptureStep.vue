<template>
  <div class="doc-capture">
    <h3 class="title">{{ title }}</h3>
    <p class="hint">{{ hint }}</p>

    <div class="mode-toggle">
      <button type="button" class="chip" :class="{ active: mode === 'camera' }" @click="setMode('camera')">
        Take photo
      </button>
      <button type="button" class="chip" :class="{ active: mode === 'upload' }" @click="setMode('upload')">
        Upload file
      </button>
    </div>

    <div v-if="mode === 'camera'" class="camera-block">
      <video v-show="!previewUrl" ref="videoRef" class="media" autoplay playsinline muted />
      <img v-if="previewUrl" :src="previewUrl" alt="Captured document" class="media" />
      <canvas ref="canvasRef" class="hidden" />

      <div class="actions">
        <button v-if="!previewUrl" type="button" class="btn" :disabled="!streamActive" @click="capture">
          Capture
        </button>
        <button v-else type="button" class="btn secondary" @click="clearPreview">Retake</button>
        <button v-if="!streamActive && !previewUrl" type="button" class="btn secondary" @click="startCamera">
          Open camera
        </button>
      </div>
      <p v-if="cameraError" class="error">{{ cameraError }}</p>
    </div>

    <div v-else>
      <ImageUpload
        :label="title"
        accept="image/jpeg,image/png"
        :max-size="5"
        @file-selected="onFileSelected"
      />
    </div>

    <div v-if="checking" class="status">Checking image quality…</div>
    <ul v-if="failures.length" class="failures">
      <li v-for="(item, idx) in failures" :key="idx">{{ item }}</li>
    </ul>
    <p v-if="passed" class="ok">Image quality looks good for OCR.</p>

    <div class="footer-actions">
      <button type="button" class="btn secondary" :disabled="busy" @click="$emit('back')">Back</button>
      <button
        type="button"
        class="btn"
        :disabled="!selectedFile || busy"
        @click="runQualityCheck"
      >
        {{ checking ? 'Checking…' : passed ? 'Continue' : 'Check quality & continue' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import ImageUpload from './ImageUpload.vue'
import { checkImageQuality } from '../services/agentService.js'

const props = defineProps({
  title: { type: String, required: true },
  hint: { type: String, default: 'Make sure the document fills the frame and text is readable.' },
  initialFile: { type: File, default: null },
})

const emit = defineEmits(['back', 'passed'])

const mode = ref('camera')
const videoRef = ref(null)
const canvasRef = ref(null)
const streamActive = ref(false)
const previewUrl = ref(null)
const cameraError = ref('')
const selectedFile = ref(null)
const checking = ref(false)
const passed = ref(false)
const failures = ref([])
const busy = ref(false)

let mediaStream = null

onMounted(() => {
  if (props.initialFile) {
    selectedFile.value = props.initialFile
    previewUrl.value = URL.createObjectURL(props.initialFile)
    mode.value = 'upload'
  } else if (navigator.mediaDevices?.getUserMedia) {
    startCamera()
  } else {
    mode.value = 'upload'
  }
})

onBeforeUnmount(() => {
  stopCamera()
  revokePreview()
})

watch(
  () => props.initialFile,
  (file) => {
    if (file) {
      selectedFile.value = file
      revokePreview()
      previewUrl.value = URL.createObjectURL(file)
    }
  }
)

function setMode(next) {
  mode.value = next
  clearPreview()
  if (next === 'camera') startCamera()
  else stopCamera()
}

async function startCamera() {
  cameraError.value = ''
  try {
    stopCamera()
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: 'environment' } },
      audio: false,
    })
    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream
    }
    streamActive.value = true
  } catch {
    cameraError.value = 'Camera unavailable. Switch to Upload file.'
    mode.value = 'upload'
    streamActive.value = false
  }
}

function stopCamera() {
  mediaStream?.getTracks().forEach((track) => track.stop())
  mediaStream = null
  streamActive.value = false
}

function revokePreview() {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = null
}

function clearPreview() {
  selectedFile.value = null
  passed.value = false
  failures.value = []
  revokePreview()
}

async function capture() {
  const video = videoRef.value
  const canvas = canvasRef.value
  if (!video || !canvas) return

  canvas.width = video.videoWidth || 1280
  canvas.height = video.videoHeight || 720
  const ctx = canvas.getContext('2d')
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

  const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.92))
  if (!blob) return

  const file = new File([blob], `document-${Date.now()}.jpg`, { type: 'image/jpeg' })
  selectedFile.value = file
  revokePreview()
  previewUrl.value = URL.createObjectURL(file)
  passed.value = false
  failures.value = []
  stopCamera()
}

function onFileSelected(file) {
  selectedFile.value = file
  passed.value = false
  failures.value = []
  revokePreview()
  if (file) previewUrl.value = URL.createObjectURL(file)
}

async function runQualityCheck() {
  if (!selectedFile.value) return

  if (passed.value) {
    emit('passed', selectedFile.value)
    return
  }

  checking.value = true
  busy.value = true
  failures.value = []
  try {
    const result = await checkImageQuality(selectedFile.value, 'document')
    if (result.passed) {
      passed.value = true
      emit('passed', selectedFile.value)
    } else {
      passed.value = false
      failures.value = result.failures?.length
        ? result.failures
        : ['Image quality is not good enough. Please retake.']
    }
  } catch (err) {
    failures.value = [err.response?.data?.error || err.message || 'Quality check failed']
  } finally {
    checking.value = false
    busy.value = false
  }
}
</script>

<style scoped>
.doc-capture {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.title {
  margin: 0;
  color: #243b53;
}

.hint {
  margin: 0;
  color: #627d98;
  font-size: 0.9rem;
}

.mode-toggle {
  display: flex;
  gap: 0.5rem;
}

.chip {
  border: 1px solid #d9e2ec;
  background: #fff;
  border-radius: 999px;
  padding: 0.4rem 0.85rem;
  cursor: pointer;
}

.chip.active {
  background: #3e7cb1;
  border-color: #3e7cb1;
  color: #fff;
}

.media {
  width: 100%;
  max-height: 320px;
  object-fit: cover;
  border-radius: 12px;
  background: #0f172a;
}

.hidden { display: none; }

.actions, .footer-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.footer-actions {
  justify-content: flex-end;
  margin-top: 0.5rem;
}

.btn {
  border: none;
  border-radius: 8px;
  padding: 0.55rem 0.9rem;
  background: #3e7cb1;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}

.btn.secondary {
  background: #edf2f7;
  color: #2d3748;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.failures {
  margin: 0;
  padding-left: 1.1rem;
  color: #c53030;
}

.ok { color: #276749; margin: 0; }
.status { color: #486581; }
.error { color: #c53030; margin: 0; }
</style>
