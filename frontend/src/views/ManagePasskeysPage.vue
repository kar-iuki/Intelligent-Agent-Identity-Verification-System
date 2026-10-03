<template>
  <main class="passkeys-page workspace">
    <router-link to="/agent/dashboard">Back to dashboard</router-link>
    <h1>Manage Passkeys</h1>
    <p>Passkeys let your device verify you. Your password and Google sign-in remain available.</p>
    <button v-if="supported" class="primary" :disabled="busy || loading" @click="add"><Fingerprint :size="20" aria-hidden="true" /> Add a passkey</button>
    <p role="status">{{ message }}</p>
    <p v-if="loading">Loading passkeys…</p>
    <p v-else-if="!passkeys.length">{{ supported ? 'No passkeys yet. Add one to sign in with Face ID or fingerprint.' : 'No passkeys yet.' }}</p>
    <ul v-else>
      <li v-for="key in passkeys" :key="key.id">
        <form v-if="editing === key.id && supported" @submit.prevent="rename(key)">
          <label :for="`label-${key.id}`">Passkey name</label>
          <input :id="`label-${key.id}`" v-model="label" maxlength="100" required />
          <button :disabled="busy">Save</button><button type="button" @click="editing = null">Cancel</button>
        </form>
        <h2 v-else>{{ key.label }}</h2>
        <p>{{ key.device_name }} — {{ key.browser }} <span v-if="localCredential === key.credential_id" class="badge">This device</span> <span v-if="key.backed_up" class="badge">Synced</span></p>
        <p>Added <time :datetime="key.created_at" :title="fullDate(key.created_at)">{{ relative(key.created_at) }}</time> · <span v-if="!key.last_used_at">Never used</span><span v-else>Last used <time :datetime="key.last_used_at" :title="fullDate(key.last_used_at)">{{ relative(key.last_used_at) }}</time></span></p>
        <div v-if="supported" class="row-actions">
          <button :disabled="busy" @click="editing = key.id; label = key.label">Rename</button>
          <button :disabled="busy" @click="removing = key">Remove</button>
        </div>
      </li>
    </ul>
    <PasskeyDialog v-if="removing" title="Remove this passkey?" @dismiss="removing = null">
      <p>You won't be able to sign in with it anymore.</p>
      <p role="status">{{ removeError }}</p>
      <div class="passkey-actions"><button :disabled="busy" @click="remove">Remove passkey</button><button @click="removing = null">Cancel</button></div>
    </PasskeyDialog>
  </main>
</template>
<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { Fingerprint } from '@lucide/vue'
import PasskeyDialog from '../components/PasskeyDialog.vue'
import { usePasskeySupport } from '../composables/usePasskeySupport.js'
import { useAuthStore } from '../stores/authStore.js'
import { registered, removeLocal, optedIn } from '../utils/passkeyStorage.js'
import { registerPasskey, isCancelled, isAborted, cancelPasskeyCeremony, signalRemoved } from '../services/passkeyService.js'
import api from '../services/api.js'
const { state } = useAuthStore()
const { supported } = usePasskeySupport()
const userId = () => state.user?.user_id
const passkeys = ref([]), loading = ref(true), busy = ref(false), message = ref(''), removing = ref(null), removeError = ref(''), editing = ref(null), label = ref(''), localCredential = ref(registered(userId())?.credentialId)
let rpId, active = true
function refreshLocal() { localCredential.value = registered(userId())?.credentialId }
async function load() {
  try {
    const { data } = await api.get('/api/auth/passkeys')
    if (!active) return
    passkeys.value = data.passkeys; rpId = data.rpId; refreshLocal()
    if (localCredential.value && !passkeys.value.some(p => p.credential_id === localCredential.value)) { removeLocal(`passkey_registered:${userId()}`); refreshLocal() }
  } catch { message.value = 'Could not load passkeys. Please reload to try again.' }
  finally { loading.value = false }
}
async function add() {
  if (busy.value) return
  busy.value = true; message.value = ''; optedIn(userId())
  try { const result = await registerPasskey(userId(), true); message.value = result.message; await load() }
  catch (error) { if (!isCancelled(error) && !isAborted(error)) message.value = 'Could not add your passkey. Please try again.' }
  finally { busy.value = false }
}
async function rename(key) {
  if (busy.value) return
  busy.value = true
  try { await api.patch(`/api/auth/passkeys/${key.id}`, { label: label.value }); editing.value = null; await load() }
  catch { message.value = 'Could not rename this passkey. Please try again.' }
  finally { busy.value = false }
}
async function remove() {
  if (busy.value || !removing.value) return
  busy.value = true; removeError.value = ''
  const key = removing.value
  try {
    await api.delete(`/api/auth/passkeys/${key.id}`)
    if (registered(userId())?.credentialId === key.credential_id) removeLocal(`passkey_registered:${userId()}`)
    removing.value = null
    message.value = "To fully delete it, also remove it from your device's passkey or password manager."
    await signalRemoved(rpId, key.credential_id); await load()
  } catch (error) { removeError.value = error.response?.data?.error || 'Could not remove this passkey. Please try again.' }
  finally { busy.value = false }
}
const fullDate = value => new Date(value).toLocaleString()
function relative(value) {
  const seconds = Math.max(0, (Date.now() - Date.parse(value)) / 1000)
  for (const [unit, size] of [['year',31536000],['month',2592000],['day',86400],['hour',3600],['minute',60]]) {
    if (seconds >= size) return new Intl.RelativeTimeFormat(undefined, { numeric:'auto' }).format(-Math.floor(seconds / size), unit)
  }
  return 'just now'
}
onMounted(() => { load(); window.addEventListener('storage', refreshLocal) })
onBeforeUnmount(() => { active = false; cancelPasskeyCeremony(); window.removeEventListener('storage', refreshLocal) })
</script>
<style scoped>
.passkeys-page { max-width:800px; margin:auto; padding:clamp(1rem,4vw,2rem); color:#243b53; }
h1 { margin:1rem 0; } h2 { font-size:1.1rem; overflow-wrap:anywhere; }
p { margin:.75rem 0; } ul { padding:0; list-style:none; } li { padding:1.25rem; margin:1rem 0; border:1px solid #d9e2ec; border-radius:12px; background:#fff; }
button { display:inline-flex; gap:.5rem; align-items:center; min-height:44px; padding:.65rem 1rem; border:1px solid #9fb3c8; border-radius:8px; background:transparent; color:inherit; cursor:pointer; }
button:disabled { opacity:.6; } .primary { background:#3e7cb1; color:white; } .row-actions { display:flex; gap:.5rem; }
input { width:100%; padding:.7rem; margin:.5rem 0; border:1px solid #9fb3c8; border-radius:6px; }
button:focus-visible, input:focus-visible, a:focus-visible { outline:3px solid #3e7cb1; outline-offset:3px; }
.badge { display:inline-block; padding:.2rem .5rem; border:1px solid #9fb3c8; border-radius:1rem; font-size:.8rem; }
</style>
