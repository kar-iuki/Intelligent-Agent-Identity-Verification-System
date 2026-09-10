<template>
  <div class="camera-capture">
    <label class="camera-label">{{ label }}</label>

    <div v-if="!supported" class="fallback">
      Camera access is not available in this browser. Please upload a selfie instead.
    </div>

    <div v-else-if="permissionDenied" class="fallback">
      Camera permission was denied. You can still upload a selfie using the file picker above.
    </div>

    <div v-else class="camera-panel">
      <video
        v-show="!capturedUrl"
        ref="videoRef"
        class="media"
        autoplay
        playsinline
        muted
      />
      <img v-if="capturedUrl" :src="capturedUrl" alt="Captured selfie" class="media" />
      <canvas ref="canvasRef" class="hidden-canvas" />

      <div class="actions">
        <button
          v-if="!capturedUrl"
          type="button"
          class="btn"
          :disabled="!streamActive"
          @click="capture"
        >
          Capture
        </button>
        <button
          v-else
          type="button"
          class="btn"
          @click="retake"
        >
          Retake
        </button>
        <button
          v-if="!streamActive && !capturedUrl"
          type="button"
          class="btn secondary"
          @click="startCamera"
        >
          Open camera
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

defineProps({
  label: {
    type: String,
    default: 'Live selfie camera',
  },
})

const emit = defineEmits(['photo-captured'])

const videoRef = ref(null)
const canvasRef = ref(null)
const streamActive = ref(false)
const capturedUrl = ref(null)
const permissionDenied = ref(false)
const supported = ref(true)

let mediaStream = null

onMounted(() => {
  supported.value = Boolean(navigator.mediaDevices?.getUserMedia)
  if (supported.value) {
    startCamera()
  }
})

onBeforeUnmount(() => {
  stopCamera()
  revokeCaptured()
})

async function startCamera() {
  permissionDenied.value = false
  revokeCaptured()

  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user' },
      audio: false,
    })

    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream
      await videoRef.value.play()
    }

    streamActive.value = true
  } catch {
    permissionDenied.value = true
    streamActive.value = false
  }
}

function stopCamera() {
  mediaStream?.getTracks().forEach((track) => track.stop())
  mediaStream = null
  streamActive.value = false

  if (videoRef.value) {
    videoRef.value.srcObject = null
  }
}

function revokeCaptured() {
  if (capturedUrl.value) {
    URL.revokeObjectURL(capturedUrl.value)
    capturedUrl.value = null
  }
}

async function capture() {
  if (!videoRef.value || !canvasRef.value) return

  const video = videoRef.value
  const canvas = canvasRef.value
  canvas.width = video.videoWidth || 640
  canvas.height = video.videoHeight || 480

  const context = canvas.getContext('2d')
  context.drawImage(video, 0, 0, canvas.width, canvas.height)

  const blob = await new Promise((resolve) => {
    canvas.toBlob(resolve, 'image/jpeg', 0.92)
  })

  if (!blob) return

  const file = new File([blob], `selfie-${Date.now()}.jpg`, { type: 'image/jpeg' })
  revokeCaptured()
  capturedUrl.value = URL.createObjectURL(file)
  stopCamera()
  emit('photo-captured', file)
}

async function retake() {
  emit('photo-captured', null)
  await startCamera()
}
</script>

<style scoped>
.camera-capture {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.camera-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #334e68;
}

.camera-panel {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.media {
  width: 100%;
  max-height: 280px;
  object-fit: cover;
  border-radius: 12px;
  background: #0f172a;
}

.actions {
  display: flex;
  gap: 0.75rem;
}

.btn {
  padding: 0.625rem 1rem;
  border: none;
  border-radius: 8px;
  background: #3e7cb1;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn.secondary {
  background: #fff;
  color: #334e68;
  border: 1px solid #d9e2ec;
}

.fallback {
  padding: 1rem;
  border-radius: 8px;
  background: #fff7ed;
  color: #9a3412;
  font-size: 0.875rem;
  line-height: 1.5;
}

.hidden-canvas {
  display: none;
}
</style>
