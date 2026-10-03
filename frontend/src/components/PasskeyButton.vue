<template>
  <button type="button" class="passkey-button" :class="{ prominent }" :disabled="busy" aria-label="Sign in with a passkey">
    <Fingerprint :size="20" aria-hidden="true" />
    <span>{{ busy ? 'Signing in…' : 'Sign in with a passkey' }}</span>
  </button>
</template>
<script setup>
import { Fingerprint } from '@lucide/vue'
defineProps({ busy: Boolean, prominent: Boolean })
</script>
<style scoped>
.passkey-button { display:flex; align-items:center; justify-content:center; gap:.6rem; width:100%; min-height:44px; padding:.75rem; border:1px solid #3e7cb1; border-radius:8px; background:transparent; color:inherit; font:inherit; font-weight:600; cursor:pointer; }
.prominent { background:#3e7cb1; color:white; }
button:disabled { opacity:.6; cursor:wait; }
button:focus-visible { outline:3px solid #3e7cb1; outline-offset:3px; }
svg { flex-shrink:0; }
</style>
