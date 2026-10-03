<template>
  <dialog ref="dialog" class="passkey-dialog" role="dialog" aria-modal="true" :aria-labelledby="titleId" @cancel.prevent="$emit('dismiss')" @close="restoreFocus">
    <button type="button" class="close" aria-label="Close dialog" @click="$emit('dismiss')">×</button>
    <h2 :id="titleId">{{ title }}</h2>
    <slot />
  </dialog>
</template>
<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
defineProps({ title: String, titleId: { type: String, default: 'passkey-dialog-title' } })
defineEmits(['dismiss'])
const dialog = ref(null)
let previousFocus
function restoreFocus() { if (previousFocus?.isConnected) previousFocus.focus() }
onMounted(() => { previousFocus = document.activeElement; dialog.value.showModal() })
onBeforeUnmount(() => { dialog.value?.close(); restoreFocus() })
// Native modal dialogs trap keyboard focus and make the background inert.
</script>
<style>
.passkey-dialog { width:min(440px, calc(100vw - 32px)); max-height:85dvh; overflow:auto; margin:auto; padding:2rem; border:1px solid #d9e2ec; border-radius:12px; background:var(--passkey-background, #fff); color:var(--passkey-color, #243b53); }
.passkey-dialog::backdrop { background:rgb(0 0 0 / .45); }
.passkey-dialog h2 { padding-right:1.5rem; margin:0 0 1rem; font-size:1.35rem; }
.passkey-dialog .close { position:absolute; top:.3rem; right:.3rem; min-width:44px; min-height:44px; background:transparent; border:0; color:inherit; font-size:1.5rem; cursor:pointer; }
.passkey-dialog button:focus-visible, .passkey-dialog a:focus-visible { outline:3px solid #3e7cb1; outline-offset:2px; }
.passkey-actions { display:flex; flex-wrap:wrap; gap:.6rem; margin-top:1rem; }
.passkey-actions button { min-height:44px; padding:.65rem 1rem; border:1px solid #9fb3c8; border-radius:8px; background:transparent; color:inherit; cursor:pointer; }
.passkey-actions .primary { background:#3e7cb1; color:white; }
.passkey-actions .text { border-color:transparent; text-decoration:underline; }
.passkey-actions button:disabled { opacity:.6; }
</style>
