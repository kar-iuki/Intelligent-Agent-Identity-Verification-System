<template>
  <div ref="captureRoot" class="doc-capture">
    <h3 class="title">{{ title }}</h3>
    <p class="hint">{{ hint }}</p>

    <div class="mode-toggle">
      <button type="button" class="chip" :class="{ active: mode === 'camera' }" @click="setMode('camera')">
        Take photo
      </button>
      <button v-if="!cameraOnly" type="button" class="chip" :class="{ active: mode === 'upload' }" @click="setMode('upload')">
        Upload file
      </button>
    </div>
    <p v-if="cameraOnly" class="hint">For this verification retry, take a new document photo. File uploads are disabled.</p>

    <div v-if="mode === 'camera'" class="camera-block">
      <!-- frame keeps the stream's aspect ratio so what you see is exactly what is captured -->
      <div class="media-frame" :style="{ '--stream-aspect': streamAspect }">
        <video
          v-show="!previewUrl"
          ref="videoRef"
          class="media"
          autoplay
          playsinline
          muted
          @loadedmetadata="updateStreamAspect"
          @resize="updateStreamAspect"
        />
        <img v-if="previewUrl" :src="previewUrl" alt="Captured document" class="media" />
      </div>
      <canvas ref="canvasRef" class="hidden" />

      <div class="actions">
        <button v-if="!streamActive && !previewUrl" type="button" class="btn secondary" @click="startCamera">
          Open camera
        </button>
        <button v-if="!previewUrl" type="button" class="btn" :disabled="!streamActive || busy" @click="capture">
          Capture
        </button>
        <button v-else type="button" class="btn secondary" :disabled="busy" @click="retake">Retake</button>
      </div>
      <p v-if="cameraError" class="error">{{ cameraError }}</p>
    </div>

    <div v-else-if="!cameraOnly">
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
    <ul v-if="warnings.length" class="warnings">
      <li v-for="(item, idx) in warnings" :key="idx">{{ item }}</li>
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
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import ImageUpload from './ImageUpload.vue'
import { checkImageQuality } from '../services/agentService.js'
import { markCameraCapture, documentCaptureSource } from '../utils/documentCaptureSource.js'

const props = defineProps({
  title: { type: String, required: true },
  hint: { type: String, default: 'Make sure the document fills the frame and text is readable.' },
  initialFile: { type: File, default: null },
  cameraOnly: { type: Boolean, default: false },
  /** national_id | passport | drivers_licence — picks the sharpness limit for the quality check */
  documentKind: { type: String, default: 'national_id' },
})

const emit = defineEmits(['back', 'passed'])

const mode = ref('camera')
const captureRoot = ref(null)
const videoRef = ref(null)
const canvasRef = ref(null)
// CSS aspect-ratio of the live stream (portrait on a phone held upright)
const streamAspect = ref(4 / 3)

function updateStreamAspect() {
  const video = videoRef.value
  if (video?.videoWidth && video?.videoHeight) {
    streamAspect.value = video.videoWidth / video.videoHeight
  }
}
const streamActive = ref(false)
const previewUrl = ref(null)
const cameraError = ref('')
const selectedFile = ref(null)
const checking = ref(false)
const passed = ref(false)
const failures = ref([])
const warnings = ref([])
const busy = ref(false)

let mediaStream = null
let cameraGeneration = 0

onMounted(() => {
  captureRoot.value?.scrollIntoView?.({ block: 'start' })
  if (props.initialFile && (!props.cameraOnly || documentCaptureSource(props.initialFile) === 'camera')) {
    selectedFile.value = props.initialFile
    previewUrl.value = URL.createObjectURL(props.initialFile)
  } else {
    startCamera()
  }
})

onBeforeUnmount(() => {
  stopCamera()
  revokePreview()
})

watch(
  () => props.initialFile,
  (file) => {
    clearPreview()
    if (file && (!props.cameraOnly || documentCaptureSource(file) === 'camera')) {
      stopCamera()
      selectedFile.value = file
      revokePreview()
      previewUrl.value = URL.createObjectURL(file)
    } else if (mode.value === 'camera') startCamera()
  }
)

watch(() => props.cameraOnly, (required) => {
  if (required && (mode.value === 'upload' || documentCaptureSource(selectedFile.value) === 'upload')) setMode('camera')
})

async function setMode(next) {
  if (busy.value || (props.cameraOnly && next === 'upload')) return
  mode.value = next
  clearPreview()
  stopCamera()
  await nextTick()
  if (next === 'camera') startCamera()
}

async function startCamera() {
  cameraError.value = ''
  stopCamera()
  const generation = cameraGeneration
  try {
    // Ask for a high-resolution stream: without this browsers default to
    // 640x480, leaving the card ~300px wide, too small for OCR of dates/ID digits.
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: { ideal: 'environment' },
        width: { ideal: 1920 },
        height: { ideal: 1080 },
      },
      audio: false,
    })
    if (generation !== cameraGeneration) {
      stream.getTracks().forEach(track => track.stop())
      return
    }
    mediaStream = stream
    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream
      updateStreamAspect()
    }
    streamActive.value = true
  } catch {
    if (generation !== cameraGeneration) return
    cameraError.value = props.cameraOnly
      ? 'Camera access is required for this retry. Allow camera permission and tap Open camera, or use a device with a camera.'
      : 'Camera unavailable. Allow camera permission or choose Upload file.'
    streamActive.value = false
  }
}

function stopCamera() {
  cameraGeneration += 1
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
  warnings.value = []
  revokePreview()
}

async function retake() {
  clearPreview()
  await startCamera()
}

async function capture() {
  const video = videoRef.value
  const canvas = canvasRef.value
  if (!video || !canvas || !streamActive.value || !video.videoWidth || !video.videoHeight) return

  canvas.width = video.videoWidth || 1280
  canvas.height = video.videoHeight || 720
  const ctx = canvas.getContext('2d')
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

  const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.92))
  if (!blob) return

  const file = markCameraCapture(new File([blob], `document-${Date.now()}.jpg`, { type: 'image/jpeg' }))
  selectedFile.value = file
  revokePreview()
  previewUrl.value = URL.createObjectURL(file)
  passed.value = false
  failures.value = []
  stopCamera()
}

function onFileSelected(file) {
  if (props.cameraOnly || busy.value) return
  selectedFile.value = file
  passed.value = false
  failures.value = []
  revokePreview()
  if (file) previewUrl.value = URL.createObjectURL(file)
}

async function runQualityCheck() {
  if (!selectedFile.value || busy.value) return
  if (props.cameraOnly && documentCaptureSource(selectedFile.value) !== 'camera') return

  if (passed.value) {
    emit('passed', selectedFile.value)
    return
  }

  checking.value = true
  busy.value = true
  failures.value = []
  try {
    const result = await checkImageQuality(selectedFile.value, 'document', props.documentKind)
    warnings.value = result.warnings || []
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
  scroll-margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.title {
  margin: 0;
  color: var(--ink);
}

.hint {
  margin: 0;
  color: var(--muted);
  font-size: 0.9rem;
}

.mode-toggle {
  display: flex;
  gap: 0.5rem;
}

.chip {
  border: 1px solid var(--line);
  background: var(--surface);
  border-radius: 999px;
  padding: 0.4rem 0.85rem;
  cursor: pointer;
}

.chip.active {
  background: var(--action);
  border-color: var(--action);
  color: var(--on-brand);
}

.media-frame {
  position: relative;
  width: min(100%, 400px, calc(32svh * var(--stream-aspect)));
  margin: 0 auto;
  aspect-ratio: var(--stream-aspect);
  border-radius: 12px;
  overflow: hidden;
  background: var(--media-background);
}

.media {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  /* letterbox rather than crop, so the full captured frame is always visible */
  object-fit: contain;
}

.hidden { display: none; }

.actions, .footer-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.footer-actions {
  margin-top: 0.5rem;
}

.btn {
  border: none;
  border-radius: 8px;
  padding: 0.55rem 0.9rem;
  background: var(--action);
  color: var(--on-brand);
  font-weight: 600;
  cursor: pointer;
}

.btn.secondary {
  background: var(--surface-muted);
  color: var(--ink);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.failures {
  margin: 0;
  padding-left: 1.1rem;
  color: var(--danger);
}

.warnings {
  margin: 0;
  padding-left: 1.1rem;
  color: var(--warning);
  font-size: 0.85rem;
}

.ok { color: var(--success); margin: 0; }
.status { color: var(--ink); }
.error { color: var(--danger); margin: 0; }
</style>
