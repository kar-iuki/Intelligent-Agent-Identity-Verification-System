<template>
  <PasskeyDialog v-if="open" title="Sign in faster next time" @dismiss="skip">
    <Fingerprint :size="32" aria-hidden="true" />
    <p>{{ hasPasskeys ? 'You have a passkey on another device. Add one on this browser too so you can sign in with Face ID or fingerprint here.' : 'Use Face ID, your fingerprint, or your screen lock instead of typing your password. Your biometric data never leaves your device.' }}</p>
    <p role="status">{{ message }}</p>
    <div class="passkey-actions">
      <button class="primary" :disabled="busy || success" @click="setup">{{ busy ? 'Setting up…' : 'Set up passkey' }}</button>
      <button @click="skip">Skip</button>
      <button class="text" @click="dismiss">Don't ask again</button>
    </div>
  </PasskeyDialog>
</template>
<script setup>
import { ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { Fingerprint } from '@lucide/vue'
import PasskeyDialog from './PasskeyDialog.vue'
import { usePasskeySupport } from '../composables/usePasskeySupport.js'
import { useAuthStore } from '../stores/authStore.js'
import { shouldPrompt, skipPrompt, dismissPrompt, registered, readLocal } from '../utils/passkeyStorage.js'
import { registerPasskey, isCancelled, isAborted, cancelPasskeyCeremony } from '../services/passkeyService.js'
import api from '../services/api.js'
const props = defineProps({ ready: Boolean })
const { state, claimPasskeyPrompt } = useAuthStore()
const { supported } = usePasskeySupport()
const open = ref(false), busy = ref(false), success = ref(false), message = ref(''), hasPasskeys = ref(false)
let active = true, checking = false, timer
const userId = () => state.user?.user_id
const eligible = () => shouldPrompt({ userId: userId(), supported: supported.value, eligible: state.passkeyPromptEligible, shown: state.passkeyPromptShown, ready: props.ready })
async function check() {
  if (checking || !eligible()) return
  checking = true
  const owner = userId()
  try {
    const { data } = await api.get('/api/auth/passkeys')
    await nextTick()
    // A paint delay lets the landing/results screen appear first.
    await new Promise(resolve => { setTimeout(resolve, 350) })
    if (!active || owner !== userId() || !eligible()) return
    hasPasskeys.value = data.passkeys.length > 0
    if (claimPasskeyPrompt()) open.value = true
  } catch { /* Optional setup never blocks the app. */ }
  finally { checking = false }
}
function close() { cancelPasskeyCeremony(); open.value = false; clearTimeout(timer) }
function skip() { if (!success.value) skipPrompt(userId()); close() }
function dismiss() { dismissPrompt(userId()); close() }
function storageChanged() {
  if (registered(userId()) || readLocal(`passkey_prompt_dismissed:${userId()}`) === true) close()
}
async function setup() {
  if (busy.value) return
  busy.value = true; message.value = ''
  try {
    const result = await registerPasskey(userId())
    success.value = true; message.value = result.message
    timer = setTimeout(close, 1800)
  } catch (error) {
    if (isCancelled(error) || isAborted(error)) close()
    else message.value = 'Could not set up your passkey. Please try again.'
  } finally { busy.value = false }
}
watch(() => [props.ready, supported.value, state.passkeyPromptEligible, state.user?.user_id], () => { if (!props.ready || !state.user) close(); check() })
onMounted(() => { window.addEventListener('storage', storageChanged); check() })
onBeforeUnmount(() => { active = false; close(); window.removeEventListener('storage', storageChanged) })
</script>
