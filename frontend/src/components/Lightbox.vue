<template>
  <div v-if="thumbnail" class="lightbox">
    <button type="button" class="thumb-btn" :aria-label="'Enlarge ' + thumbnail.alt" @click="openLightbox">
      <img :src="thumbnail.url" :alt="thumbnail.alt" class="thumb" />
      <span class="expand-mark" aria-hidden="true"><Maximize2 :size="16" /></span>
    </button>
    <dialog ref="dialog" class="viewer" aria-label="Document viewer"
      @keydown.left.prevent="move(-1)" @keydown.right.prevent="move(1)"
      @click.self="dialog.close()">
      <div v-if="current" class="viewer-frame">
        <header>
          <strong aria-live="polite">{{ current.alt }}</strong>
          <button type="button" aria-label="Close viewer" autofocus @click="dialog.close()"><X :size="20" /></button>
        </header>
        <img :src="current.url" :alt="current.alt" class="full" />
        <footer v-if="gallery.length > 1">
          <button type="button" aria-label="Previous image" @click="move(-1)"><ChevronLeft :size="20" /></button>
          <span>{{ index + 1 }} / {{ gallery.length }}</span>
          <button type="button" aria-label="Next image" @click="move(1)"><ChevronRight :size="20" /></button>
        </footer>
      </div>
    </dialog>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ChevronLeft, ChevronRight, Maximize2, X } from '@lucide/vue'

const props = defineProps({
  imageUrl: { type: String, default: '' },
  alt: { type: String, default: 'Image' },
  images: { type: Array, default: () => [] },
  startIndex: { type: Number, default: 0 },
})
const dialog = ref(null)
const index = ref(0)
const gallery = computed(() => props.images.length ? props.images : props.imageUrl ? [{ url: props.imageUrl, alt: props.alt }] : [])
const thumbnail = computed(() => gallery.value[props.startIndex] || gallery.value[0])
const current = computed(() => gallery.value[index.value] || thumbnail.value)

function openLightbox() {
  index.value = gallery.value.indexOf(thumbnail.value)
  dialog.value?.showModal()
}
function move(step) {
  const count = gallery.value.length
  if (count) index.value = (index.value + step + count) % count
}
defineExpose({ openLightbox })
</script>

<style scoped>
.thumb-btn {
  position: relative;
  width: 100%;
  padding: 0;
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
  background: var(--media-background);
  cursor: zoom-in;
}
.thumb { display: block; width: 100%; height: 144px; object-fit: contain; }
.expand-mark {
  position: absolute; inset: auto 8px 8px auto; display: grid; place-items: center;
  width: 28px; height: 28px; border-radius: 6px; color: #fff; background: #111613db;
}
.viewer {
  position: fixed; inset: 0; margin: auto; padding: 0; width: min(60rem, calc(100% - 24px));
  max-height: calc(100dvh - 24px); overflow: auto; border: 1px solid var(--sidebar-border);
  border-radius: 12px; background: var(--media-background); color: var(--sidebar-text);
}
.viewer::backdrop { background: rgb(9 15 11 / 85%); }
.viewer-frame header, .viewer-frame footer { display: flex; align-items: center; gap: 16px; padding: 8px 12px; }
.viewer-frame header { justify-content: space-between; border-bottom: 1px solid var(--sidebar-border); }
.viewer-frame strong { font-size: 15px; font-weight: 550; }
.full { display: block; width: 100%; height: min(65dvh, 720px); object-fit: contain; }
.viewer-frame footer { justify-content: center; border-top: 1px solid var(--sidebar-border); font: 13px var(--meta-font); }
.viewer-frame button {
  display: grid; place-items: center; width: 44px; height: 44px; border: 0;
  border-radius: 8px; color: inherit; background: transparent;
}
.viewer-frame button:hover { background: var(--sidebar-hover); }
</style>
