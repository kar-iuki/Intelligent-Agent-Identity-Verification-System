<template>
  <div ref="captureRoot" class="doc-capture">
    <div v-if="!cameraOnly" class="source-switch" role="group" aria-label="Image source">
      <button type="button" :aria-pressed="mode === 'camera'" :disabled="busy" @click="setMode('camera')">Take photo</button>
      <button type="button" :aria-pressed="mode === 'upload'" :disabled="busy" @click="setMode('upload')">Upload file</button>
    </div>
    <div v-if="mode === 'camera'" class="capture-console" :data-layout="layout">
      <div class="capture-toolbar">
        <span class="capture-label">Document camera</span>
        <div class="capture-switch" role="group" aria-label="Capture layout">
          <button v-for="view in ['guided','focus']" :key="view" type="button" :aria-pressed="layout === view" @click="selectLayout(view)">{{ view === 'guided' ? 'Guided' : 'Focus' }}</button>
        </div>
      </div>
      <div class="capture-body">
        <div class="capture-copy">
          <h3 class="title">{{ title }}</h3>
          <p>{{ previewUrl ? 'Check that the smallest print is legible and every edge is visible.' : hint }}</p>
        </div>
        <div class="capture-scene live-scene">
          <div class="media-frame" :style="{ '--stream-aspect': streamAspect }">
            <video v-show="!previewUrl" ref="videoRef" class="media" :class="{ flipped: flipDocument }" autoplay playsinline muted @loadedmetadata="updateStreamAspect" @resize="updateStreamAspect" />
            <img v-if="previewUrl" :src="previewUrl" alt="Captured document" class="media" @load="updatePhotoAspect" />
            <div v-if="streamActive && !previewUrl" class="capture-marks" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
          </div>
          <span v-if="!streamActive && !previewUrl" class="camera-standby" role="status">{{ cameraError ? 'Camera unavailable' : 'Waiting for camera…' }}</span>
          <canvas ref="canvasRef" class="hidden" />
        </div>
        <div class="capture-operations">
          <button v-if="previewUrl" type="button" class="capture-secondary" :disabled="busy" @click="retake">Retake</button>
          <template v-else>
            <button type="button" class="capture-primary" :disabled="!streamActive || busy" @click="capture">Capture</button>
            <button v-if="streamActive" type="button" class="capture-secondary flip-control"
              :aria-pressed="flipDocument" title="Use this if the document text looks backwards"
              @click="toggleDocumentFlip">Flip horizontally</button>
            <button v-if="cameraError" type="button" class="capture-secondary" @click="startCamera">Open camera</button>
          </template>
        </div>
      </div>
    </div>
    <div v-else-if="!cameraOnly">
      <h3 class="title">{{ title }}</h3>
      <p class="upload-hint">{{ hint }}</p>
      <div :inert="busy"><ImageUpload :label="title" accept="image/jpeg,image/png" :max-size="5" @file-selected="onFileSelected" /></div>
    </div>
    <p v-if="mode === 'camera' && cameraError" class="notice" role="alert">{{ cameraError }}</p>
    <div v-if="failures.length" class="notice" role="alert">
      <strong>{{ checkUnavailable ? 'Quality check unavailable' : 'Your photo needs another look' }}</strong>
      <ul><li v-for="item in failures" :key="item">{{ item }}</li></ul>
    </div>
    <ul v-if="warnings.length" class="notice"><li v-for="item in warnings" :key="item">{{ item }}</li></ul>
    <p v-if="checking || passed" role="status">{{ checking ? 'Checking image quality…' : 'Photo quality check passed.' }}</p>
    <div class="footer-actions">
      <button type="button" class="step-back" :disabled="busy" @click="$emit('back')">Back</button>
      <button type="button" class="step-next" :disabled="!selectedFile || busy" @click="runQualityCheck">{{ checking ? 'Checking…' : passed ? 'Continue' : 'Check quality & continue' }}</button>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import '../capture.css'
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
const layout = ref('focus')
const checkUnavailable = ref(false)
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
function updatePhotoAspect(event) {
  const img = event.currentTarget
  if (img.naturalWidth && img.naturalHeight) streamAspect.value = img.naturalWidth / img.naturalHeight
}
const flipDocument = ref(false)
let flipPreferenceKey = ''

function toggleDocumentFlip() {
  flipDocument.value = !flipDocument.value
  try { sessionStorage.setItem(flipPreferenceKey, String(flipDocument.value)) } catch {}
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
let qualityGeneration = 0

onMounted(() => {
  try {
    if (sessionStorage.getItem('verity-capture-layout') === 'guided') layout.value = 'guided'
  } catch { /* Camera capture also works when session storage is unavailable. */ }
  captureRoot.value?.scrollIntoView?.({ block: 'start' })
  if (props.initialFile && (!props.cameraOnly || documentCaptureSource(props.initialFile) === 'camera')) {
    selectedFile.value = props.initialFile
    previewUrl.value = URL.createObjectURL(props.initialFile)
  } else {
    startCamera()
  }
})

onBeforeUnmount(() => {
  qualityGeneration += 1
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
  if (required && (mode.value === 'upload' || documentCaptureSource(selectedFile.value) === 'upload')) {
    clearPreview()
    mode.value = 'camera'
    nextTick(startCamera)
  }
})

function selectLayout(view) {
  layout.value = view
  try { sessionStorage.setItem('verity-capture-layout', view) } catch {}
}

async function setMode(next) {
  if (busy.value || next === mode.value || (props.cameraOnly && next === 'upload')) return
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
    const deviceId = stream.getVideoTracks?.()[0]?.getSettings?.().deviceId || 'default'
    const preferenceKey = 'verity-document-flip:' + deviceId
    if (flipPreferenceKey !== preferenceKey) {
      flipPreferenceKey = preferenceKey
      flipDocument.value = false
      try { flipDocument.value = sessionStorage.getItem(preferenceKey) === 'true' } catch {}
    }
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
  qualityGeneration += 1
  checking.value = false
  busy.value = false
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
  const flipped = flipDocument.value
  if (flipped) ctx.setTransform(-1, 0, 0, 1, canvas.width, 0)
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

  const generation = cameraGeneration
  const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.92))
  if (!blob || generation !== cameraGeneration || flipped !== flipDocument.value) return

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
  warnings.value = []
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

  const generation = ++qualityGeneration
  checkUnavailable.value = false
  warnings.value = []
  checking.value = true
  busy.value = true
  failures.value = []
  try {
    const result = await checkImageQuality(selectedFile.value, 'document', props.documentKind)
    if (generation !== qualityGeneration) return
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
    if (generation !== qualityGeneration) return
    checkUnavailable.value = true
    failures.value = [err.response?.data?.error || err.message || 'Try the quality check again.']
  } finally {
    if (generation === qualityGeneration) {
      checking.value = false
      busy.value = false
    }
  }
}
</script>

<style scoped>
.doc-capture { scroll-margin-top:1rem; display:grid; gap:12px; max-width:680px; margin-inline:auto; }
.source-switch { display:flex; gap:4px; }
.source-switch button,.footer-actions button { min-height:44px; padding:8px 16px; font:inherit; font-weight:600; border-radius:24px; }
.source-switch button,.step-back { background:var(--surface); color:var(--ink); border:1px solid var(--line); }
.source-switch button[aria-pressed="true"] { background:var(--selected-bg); color:var(--selected-text); border-color:var(--selected-border); }
.live-scene { display:grid; place-items:center; min-height:108px; }
.media-frame { position:relative; width:min(100%, 560px, calc(32svh * var(--stream-aspect))); aspect-ratio:var(--stream-aspect); margin:auto; }
.media { position:absolute; inset:0; width:100%; height:100%; object-fit:contain; }
.media.flipped { transform:scaleX(-1); }
.flip-control[aria-pressed="true"] { background:var(--fg); color:var(--panel); border-radius:8px; }
.hidden { display:none; }
.camera-standby { position:absolute; left:12px; right:12px; text-align:center; color:#e4ebe1; font-size:14px; }
.footer-actions { display:flex; flex-wrap:wrap; justify-content:space-between; gap:8px; }
.step-next { background:var(--action); border:1px solid var(--action); color:var(--on-brand); }
.step-next:hover:not(:disabled) { background:var(--action-hover); }
.notice { padding:12px 16px; border-left:3px solid var(--warning-border); color:var(--warning); background:var(--warning-bg); font-size:14px; }
.notice ul { padding-left:18px; margin-top:4px; }
.upload-hint { color:var(--muted); margin-block:5px 12px; }
</style>
