<template>
  <div class="lightbox">
    <button type="button" class="thumb-btn" @click="open = true">
      <img :src="currentUrl" :alt="currentAlt" class="thumb" />
    </button>

    <Teleport to="body">
      <div
        v-if="open"
        class="overlay"
        @click.self="close"
      >
        <button type="button" class="close" aria-label="Close" @click="close">×</button>

        <button
          v-if="images.length > 1"
          type="button"
          class="nav prev"
          aria-label="Previous"
          @click="prev"
        >
          ‹
        </button>

        <img :src="currentUrl" :alt="currentAlt" class="full" />

        <button
          v-if="images.length > 1"
          type="button"
          class="nav next"
          aria-label="Next"
          @click="next"
        >
          ›
        </button>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  imageUrl: {
    type: String,
    default: '',
  },
  alt: {
    type: String,
    default: 'Image',
  },
  images: {
    type: Array,
    default: () => [],
  },
  startIndex: {
    type: Number,
    default: 0,
  },
})

const open = ref(false)
const index = ref(props.startIndex)

const resolvedImages = computed(() => {
  if (props.images?.length) return props.images
  if (props.imageUrl) return [{ url: props.imageUrl, alt: props.alt }]
  return []
})

const currentUrl = computed(() => resolvedImages.value[index.value]?.url || props.imageUrl)
const currentAlt = computed(() => resolvedImages.value[index.value]?.alt || props.alt)

watch(
  () => props.startIndex,
  (value) => {
    index.value = value
  }
)

function close() {
  open.value = false
}

function next() {
  if (!resolvedImages.value.length) return
  index.value = (index.value + 1) % resolvedImages.value.length
}

function prev() {
  if (!resolvedImages.value.length) return
  index.value = (index.value - 1 + resolvedImages.value.length) % resolvedImages.value.length
}

function onKeydown(event) {
  if (!open.value) return
  if (event.key === 'Escape') close()
  if (event.key === 'ArrowRight') next()
  if (event.key === 'ArrowLeft') prev()
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
})

defineExpose({ openLightbox: () => { open.value = true } })
</script>

<style scoped>
.thumb-btn {
  border: none;
  padding: 0;
  background: transparent;
  cursor: pointer;
  width: 100%;
}

.thumb {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: 10px;
  display: block;
  background: #0f172a;
}

.overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.88);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.full {
  max-width: min(90vw, 1100px);
  max-height: 85vh;
  object-fit: contain;
  border-radius: 8px;
}

.close {
  position: absolute;
  top: 1rem;
  right: 1.25rem;
  border: none;
  background: transparent;
  color: #fff;
  font-size: 2rem;
  cursor: pointer;
}

.nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  border: none;
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  font-size: 2rem;
  width: 48px;
  height: 48px;
  border-radius: 999px;
  cursor: pointer;
}

.nav.prev { left: 1.5rem; }
.nav.next { right: 1.5rem; }
</style>
