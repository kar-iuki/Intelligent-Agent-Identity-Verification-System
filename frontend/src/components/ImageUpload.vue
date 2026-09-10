<template>
  <div class="image-upload">
    <label class="upload-label">{{ label }}</label>

    <div
      class="drop-zone"
      :class="{ 'drag-over': isDragging, 'has-preview': !!previewUrl }"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      @click="triggerBrowse"
    >
      <img v-if="previewUrl" :src="previewUrl" alt="Selected preview" class="preview" />

      <div v-else class="drop-placeholder">
        <p>Drag and drop an image here</p>
        <p class="hint">JPEG or PNG · max {{ maxSize }}MB</p>
        <button type="button" class="browse-btn" @click.stop="triggerBrowse">Browse</button>
      </div>
    </div>

    <input
      ref="fileInput"
      type="file"
      class="hidden-input"
      :accept="accept"
      @change="handleFileInput"
    />

    <p v-if="error" class="error">{{ error }}</p>

    <button
      v-if="previewUrl"
      type="button"
      class="clear-btn"
      @click="clearSelection"
    >
      Remove image
    </button>
  </div>
</template>

<script setup>
import { ref, watch, onBeforeUnmount } from 'vue'

const props = defineProps({
  label: {
    type: String,
    required: true,
  },
  accept: {
    type: String,
    default: 'image/jpeg,image/png',
  },
  maxSize: {
    type: Number,
    default: 5,
  },
  modelValue: {
    type: File,
    default: null,
  },
})

const emit = defineEmits(['file-selected', 'update:modelValue'])

const fileInput = ref(null)
const previewUrl = ref(null)
const error = ref('')
const isDragging = ref(false)

watch(
  () => props.modelValue,
  (file) => {
    if (!file) {
      revokePreview()
      return
    }
    setPreview(file)
  }
)

onBeforeUnmount(() => {
  revokePreview()
})

function triggerBrowse() {
  fileInput.value?.click()
}

function handleDrop(event) {
  isDragging.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file) validateAndSelect(file)
}

function handleFileInput(event) {
  const file = event.target.files?.[0]
  if (file) validateAndSelect(file)
  event.target.value = ''
}

function validateAndSelect(file) {
  error.value = ''

  const allowed = props.accept.split(',').map((type) => type.trim())
  if (!allowed.includes(file.type)) {
    error.value = 'Only JPEG and PNG images are allowed'
    return
  }

  const maxBytes = props.maxSize * 1024 * 1024
  if (file.size > maxBytes) {
    error.value = `File must be ${props.maxSize}MB or smaller`
    return
  }

  setPreview(file)
  emit('file-selected', file)
  emit('update:modelValue', file)
}

function setPreview(file) {
  revokePreview()
  previewUrl.value = URL.createObjectURL(file)
}

function revokePreview() {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = null
  }
}

function clearSelection() {
  revokePreview()
  error.value = ''
  emit('file-selected', null)
  emit('update:modelValue', null)
}
</script>

<style scoped>
.image-upload {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.upload-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #334e68;
}

.drop-zone {
  border: 2px dashed #bcccdc;
  border-radius: 12px;
  min-height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background: #f8fafc;
  overflow: hidden;
  transition: border-color 0.2s, background-color 0.2s;
}

.drop-zone.drag-over {
  border-color: #3e7cb1;
  background: #e3f0fa;
}

.drop-zone.has-preview {
  border-style: solid;
  padding: 0;
}

.drop-placeholder {
  text-align: center;
  color: #627d98;
  padding: 1.5rem;
}

.hint {
  font-size: 0.8125rem;
  color: #9fb3c8;
  margin: 0.35rem 0 1rem;
}

.browse-btn,
.clear-btn {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: 1px solid #d9e2ec;
  background: #fff;
  color: #334e68;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
}

.browse-btn:hover,
.clear-btn:hover {
  background: #f0f4f8;
}

.preview {
  width: 100%;
  max-height: 260px;
  object-fit: contain;
  display: block;
  background: #0f172a;
}

.hidden-input {
  display: none;
}

.error {
  color: #c81e1e;
  font-size: 0.8125rem;
}
</style>
