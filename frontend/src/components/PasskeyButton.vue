<template>
  <button type="button" class="passkey-button" :class="{ prominent, 'icon-only': iconOnly }" :disabled="busy" :aria-busy="busy" aria-label="Sign in with a passkey" title="Sign in with a passkey">
    <Fingerprint :size="20" aria-hidden="true" />
    <span v-if="!iconOnly">{{ busy ? 'Signing in…' : 'Sign in with a passkey' }}</span>
  </button>
</template>
<script setup>
import { Fingerprint } from '@lucide/vue'
defineProps({ busy: Boolean, prominent: Boolean, iconOnly: Boolean })
</script>
<style scoped>
.passkey-button { display:flex; align-items:center; justify-content:center; gap:.6rem; width:100%; min-height:44px; padding:.75rem; border:1px solid var(--action); border-radius:8px; background:transparent; color:inherit; font:inherit; font-weight:600; cursor:pointer; }
.prominent { background:var(--action); color:var(--on-brand); }
.icon-only { width:48px; height:48px; flex:0 0 48px; padding:0; border-color:var(--line); color:var(--link); background:var(--surface-muted); }
button:disabled { opacity:.6; cursor:wait; }
button:focus-visible { outline:3px solid var(--focus); outline-offset:3px; }
svg { flex-shrink:0; }
</style>
