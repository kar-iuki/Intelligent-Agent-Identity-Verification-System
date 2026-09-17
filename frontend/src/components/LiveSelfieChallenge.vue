<template>
  <div class="live-selfie">
    <h3 class="title">Live selfie check</h3>
    <p class="hint">
      First we take a clear photo while your face is centred and still.
      Then you follow a short movement so we know you are a real person
      (not a photo held up to the camera).
    </p>

    <div class="challenge-banner" :class="statusClass">
      <strong>{{ bannerTitle }}</strong>
      <span>{{ statusText }}</span>
    </div>

    <div class="stage">
      <video v-show="phase !== 'success'" ref="videoRef" class="media" autoplay playsinline muted />
      <img
        v-if="previewUrl && phase === 'success'"
        :src="previewUrl"
        alt="Captured selfie"
        class="media preview"
      />
      <canvas ref="overlayRef" class="overlay" />
      <canvas ref="captureRef" class="hidden" />
      <div v-if="phase === 'center'" class="guide-oval" :class="{ ready: faceCentered }" />
      <div v-if="phase === 'challenge' && previewUrl" class="thumb-wrap">
        <img :src="previewUrl" alt="Saved selfie" class="thumb" />
        <span>Saved photo</span>
      </div>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loadingModel" class="muted">Loading face tracker…</p>

    <div class="actions">
      <button type="button" class="btn secondary" :disabled="busy" @click="$emit('back')">Back</button>
      <button
        type="button"
        class="btn secondary"
        :disabled="busy || loadingModel"
        @click="restartChallenge"
      >
        Start over
      </button>
      <button
        v-if="phase === 'center'"
        type="button"
        class="btn"
        :disabled="!faceCentered || busy || loadingModel"
        @click="captureCenteredSelfie"
      >
        Take photo
      </button>
      <button
        v-if="phase === 'success'"
        type="button"
        class="btn"
        @click="emitPassed"
      >
        Continue
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import {
  FaceLandmarker,
  FilesetResolver,
  DrawingUtils,
} from '@mediapipe/tasks-vision'

const emit = defineEmits(['back', 'passed'])

const videoRef = ref(null)
const overlayRef = ref(null)
const captureRef = ref(null)
const loadingModel = ref(true)
const error = ref('')
const busy = ref(false)
const challenge = ref('turn_left')
/** loading | center | challenge | success */
const phase = ref('loading')
const completedFile = ref(null)
const previewUrl = ref(null)
const faceCentered = ref(false)
const blinkClosed = ref(false)
const yawBaseline = ref(null)

let faceLandmarker = null
let mediaStream = null
let rafId = null
let lastVideoTime = -1
let blinkCount = 0
let centeredSince = null
let latestLandmarks = null

const CHALLENGES = ['blink', 'turn_left', 'turn_right']

const bannerTitle = computed(() => {
  if (phase.value === 'center') return 'Step 1 — Centre your face'
  if (phase.value === 'challenge') {
    if (challenge.value === 'blink') return 'Step 2 — Blink twice'
    if (challenge.value === 'turn_left') return 'Step 2 — Turn your head left'
    return 'Step 2 — Turn your head right'
  }
  if (phase.value === 'success') return 'Done'
  return 'Preparing'
})

const statusText = computed(() => {
  if (loadingModel.value) return 'Preparing camera…'
  if (phase.value === 'center') {
    return faceCentered.value
      ? 'Face looks centred — hold still, then tap Take photo.'
      : 'Look straight at the camera and place your face inside the oval.'
  }
  if (phase.value === 'challenge') {
    if (challenge.value === 'blink') {
      return blinkClosed.value ? 'Open your eyes…' : 'Close your eyes, then open them.'
    }
    if (challenge.value === 'turn_left') return 'Slowly look to your left (photo already saved).'
    return 'Slowly look to your right (photo already saved).'
  }
  if (phase.value === 'success') return 'Liveness confirmed — using your centred selfie.'
  return ''
})

const statusClass = computed(() => {
  if (phase.value === 'success') return 'ok'
  if (phase.value === 'center' && faceCentered.value) return 'ready'
  return 'active'
})

onMounted(async () => {
  pickChallenge()
  try {
    await initLandmarker()
    await startCamera()
    loadingModel.value = false
    phase.value = 'center'
    loop()
  } catch (err) {
    loadingModel.value = false
    error.value = err.message || 'Could not start live selfie camera'
  }
})

onBeforeUnmount(() => {
  stop()
  revokePreview()
})

function pickChallenge() {
  challenge.value = CHALLENGES[Math.floor(Math.random() * CHALLENGES.length)]
  blinkClosed.value = false
  yawBaseline.value = null
  blinkCount = 0
  centeredSince = null
  faceCentered.value = false
}

function restartChallenge() {
  revokePreview()
  completedFile.value = null
  pickChallenge()
  phase.value = 'center'
  error.value = ''
}

async function initLandmarker() {
  const vision = await FilesetResolver.forVisionTasks(
    'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@1.0.1/wasm'
  )
  faceLandmarker = await FaceLandmarker.createFromOptions(vision, {
    baseOptions: {
      modelAssetPath:
        'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task',
      delegate: 'GPU',
    },
    runningMode: 'VIDEO',
    numFaces: 1,
  })
}

async function startCamera() {
  mediaStream = await navigator.mediaDevices.getUserMedia({
    video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } },
    audio: false,
  })
  if (videoRef.value) {
    videoRef.value.srcObject = mediaStream
    await videoRef.value.play()
  }
}

function stop() {
  if (rafId) cancelAnimationFrame(rafId)
  mediaStream?.getTracks().forEach((t) => t.stop())
  mediaStream = null
  faceLandmarker?.close?.()
  faceLandmarker = null
}

function revokePreview() {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = null
}

function loop() {
  rafId = requestAnimationFrame(loop)
  const video = videoRef.value
  if (!video || !faceLandmarker || video.readyState < 2) return
  if (phase.value === 'success') return

  const now = performance.now()
  if (video.currentTime === lastVideoTime) return
  lastVideoTime = video.currentTime

  const result = faceLandmarker.detectForVideo(video, now)
  drawOverlay(result)

  if (!result.faceLandmarks?.length) {
    error.value = 'Keep your face inside the frame'
    faceCentered.value = false
    centeredSince = null
    latestLandmarks = null
    return
  }

  error.value = ''
  const landmarks = result.faceLandmarks[0]
  latestLandmarks = landmarks

  if (phase.value === 'center') {
    updateCenterStatus(landmarks, now)
    return
  }

  if (phase.value === 'challenge') {
    evaluateChallenge(landmarks)
  }
}

function isFaceCentered(landmarks) {
  // Approximate face box from cheeks + forehead / chin landmarks
  const xs = [landmarks[33].x, landmarks[263].x, landmarks[1].x, landmarks[234].x, landmarks[454].x]
  const ys = [landmarks[10].y, landmarks[152].y, landmarks[1].y]
  const minX = Math.min(...xs)
  const maxX = Math.max(...xs)
  const minY = Math.min(...ys)
  const maxY = Math.max(...ys)
  const cx = (minX + maxX) / 2
  const cy = (minY + maxY) / 2
  const width = maxX - minX
  const height = maxY - minY

  const inCenter = Math.abs(cx - 0.5) < 0.12 && Math.abs(cy - 0.48) < 0.14
  const reasonableSize = width > 0.18 && width < 0.72 && height > 0.22 && height < 0.85
  // Prefer facing camera roughly straight for a sharp portrait
  const yaw = Math.abs(estimateYaw(landmarks))
  const facingForward = yaw < 0.04

  return inCenter && reasonableSize && facingForward
}

function updateCenterStatus(landmarks, now) {
  const centered = isFaceCentered(landmarks)
  faceCentered.value = centered
  if (!centered) {
    centeredSince = null
    return
  }
  if (centeredSince == null) centeredSince = now
  // Optional auto-capture after holding still ~1.2s
  if (now - centeredSince > 1200 && !busy.value && !completedFile.value) {
    captureCenteredSelfie()
  }
}

function eyeAspectRatio(landmarks, indices) {
  const dist = (a, b) => {
    const dx = landmarks[a].x - landmarks[b].x
    const dy = landmarks[a].y - landmarks[b].y
    return Math.hypot(dx, dy)
  }
  const [p1, p2, p3, p4, p5, p6] = indices
  return (dist(p2, p6) + dist(p3, p5)) / (2 * dist(p1, p4) + 1e-6)
}

function estimateYaw(landmarks) {
  // Positive yaw ≈ face turned toward subject's left (camera right)
  const leftCheek = landmarks[234]
  const rightCheek = landmarks[454]
  const nose = landmarks[1]
  const midX = (leftCheek.x + rightCheek.x) / 2
  return nose.x - midX
}

function evaluateChallenge(landmarks) {
  if (challenge.value === 'blink') {
    const leftEar = eyeAspectRatio(landmarks, [33, 160, 158, 133, 153, 144])
    const rightEar = eyeAspectRatio(landmarks, [362, 385, 387, 263, 373, 380])
    const ear = (leftEar + rightEar) / 2

    if (!blinkClosed.value && ear < 0.16) {
      blinkClosed.value = true
    } else if (blinkClosed.value && ear > 0.22) {
      blinkClosed.value = false
      blinkCount += 1
      if (blinkCount >= 2) finishChallenge()
    }
    return
  }

  const yaw = estimateYaw(landmarks)
  if (yawBaseline.value === null) {
    // Baseline should be near-centre facing after photo
    yawBaseline.value = yaw
    return
  }

  const delta = yaw - yawBaseline.value
  if (challenge.value === 'turn_left' && delta > 0.045) {
    finishChallenge()
  }
  if (challenge.value === 'turn_right' && delta < -0.045) {
    finishChallenge()
  }
}

async function captureCenteredSelfie() {
  if (busy.value || phase.value !== 'center') return
  if (!faceCentered.value && !latestLandmarks) {
    error.value = 'Centre your face in the oval first'
    return
  }

  busy.value = true
  error.value = ''

  try {
    const video = videoRef.value
    const canvas = captureRef.value
    if (!video || !canvas) return

    canvas.width = video.videoWidth || 1280
    canvas.height = video.videoHeight || 720
    const ctx = canvas.getContext('2d')
    ctx.setTransform(1, 0, 0, 1, 0, 0)
    // Mirror capture to match selfie preview expectation
    ctx.translate(canvas.width, 0)
    ctx.scale(-1, 1)
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

    const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.92))
    if (!blob) {
      error.value = 'Could not capture photo — try again'
      return
    }

    revokePreview()
    completedFile.value = new File([blob], `live-selfie-${Date.now()}.jpg`, { type: 'image/jpeg' })
    previewUrl.value = URL.createObjectURL(completedFile.value)

    blinkCount = 0
    blinkClosed.value = false
    yawBaseline.value = null
    phase.value = 'challenge'
  } finally {
    busy.value = false
  }
}

function finishChallenge() {
  if (phase.value !== 'challenge' || !completedFile.value) return
  phase.value = 'success'
  blinkCount = 0
}

function drawOverlay(result) {
  const canvas = overlayRef.value
  const video = videoRef.value
  if (!canvas || !video) return
  canvas.width = video.clientWidth
  canvas.height = video.clientHeight
  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  if (phase.value !== 'center' && phase.value !== 'challenge') return
  if (!result.faceLandmarks?.length) return

  const drawingUtils = new DrawingUtils(ctx)
  for (const landmarks of result.faceLandmarks) {
    drawingUtils.drawConnectors(landmarks, FaceLandmarker.FACE_LANDMARKS_TESSELATION, {
      color: 'rgba(62, 124, 177, 0.25)',
      lineWidth: 0.5,
    })
  }
}

function emitPassed() {
  if (!completedFile.value) return
  emit('passed', {
    file: completedFile.value,
    challenge: challenge.value,
  })
}
</script>

<style scoped>
.live-selfie {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.title { margin: 0; color: #243b53; }
.hint { margin: 0; color: #627d98; font-size: 0.9rem; }

.challenge-banner {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  padding: 0.85rem 1rem;
  border-radius: 10px;
  background: #ebf8ff;
  border: 1px solid #90cdf4;
  color: #2a4365;
}

.challenge-banner.ready {
  background: #f0fff4;
  border-color: #9ae6b4;
  color: #276749;
}

.challenge-banner.ok {
  background: #c6f6d5;
  border-color: #9ae6b4;
  color: #276749;
}

.stage {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  background: #0f172a;
}

.media {
  width: 100%;
  max-height: 420px;
  display: block;
  transform: scaleX(-1);
  object-fit: cover;
}

.media.preview {
  transform: none;
}

.overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  transform: scaleX(-1);
}

.guide-oval {
  position: absolute;
  left: 50%;
  top: 46%;
  width: min(52%, 220px);
  aspect-ratio: 3 / 4;
  transform: translate(-50%, -50%);
  border: 2px dashed rgba(255, 255, 255, 0.55);
  border-radius: 50%;
  pointer-events: none;
  box-shadow: 0 0 0 9999px rgba(15, 23, 42, 0.35);
}

.guide-oval.ready {
  border-color: #68d391;
  border-style: solid;
}

.thumb-wrap {
  position: absolute;
  right: 0.75rem;
  bottom: 0.75rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  padding: 0.35rem;
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.75);
  color: #e2e8f0;
  font-size: 0.7rem;
}

.thumb {
  width: 64px;
  height: 80px;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.35);
}

.hidden { display: none; }

.actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: flex-end;
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

.error { color: #c53030; margin: 0; }
.muted { color: #718096; margin: 0; }
</style>
