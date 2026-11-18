<template>
  <div class="platform workspace">
    <header><div><h1>My workspace</h1><p class="subtitle">Your verification and account activity.</p></div></header>
    <PasskeyPrompt :ready="status === 'verified'" />
    <main class="platform-content">
      <section class="identity-summary" aria-labelledby="summary-title">
        <div class="summary-label"><ShieldCheck :size="21" /><span>Identity verification</span></div>
        <div aria-live="polite"><h2 id="summary-title">{{ summary.title }}</h2><p>{{ summary.detail }}</p></div>
        <div class="summary-actions"><RouterLink to="/agent/dashboard">{{ summary.action }} <ArrowRight :size="17" /></RouterLink><button v-if="status === 'unavailable'" @click="loadStatus">Retry</button></div>
      </section>
      <div class="workspace-tools">
        <RouterLink to="/agent/audit"><History /><div><h2>Activity history</h2><p>Review actions and outcomes on your account.</p></div><ArrowRight :size="18" /></RouterLink>
        <RouterLink to="/agent/passkeys"><Fingerprint /><div><h2>Passkeys &amp; security</h2><p>Manage the devices you use to sign in.</p></div><ArrowRight :size="18" /></RouterLink>
      </div>
    </main>
  </div>
</template>
<script setup>
import { computed, onMounted, ref } from 'vue'
import { ArrowRight, Fingerprint, History, ShieldCheck } from '@lucide/vue'
import PasskeyPrompt from '../components/PasskeyPrompt.vue'
import { getVerificationStatus } from '../services/verificationService.js'

const status = ref('loading')
const summaries = {
  loading: { title:'Checking your status…', detail:'Retrieving your latest verification record.', action:'Open identity overview' },
  not_started: { title:'Verification not yet submitted', detail:'Continue your registration to submit your photo ID and live selfie.', action:'Continue registration' },
  pending: { title:'Verification in progress', detail:'Open your overview to follow the checks and see any next steps.', action:'View progress' },
  verified: { title:'Your identity is verified', detail:'Your verification result is available in your identity overview.', action:'View result' },
  review: { title:'Awaiting review', detail:'Your submission is in the review queue. Your overview shows the latest outcome.', action:'View submission' },
  rejected: { title:'Verification unsuccessful', detail:'Read the feedback in your overview and check which next steps are available.', action:'View feedback' },
  unavailable: { title:'Status unavailable', detail:'The latest verification record could not be loaded.', action:'Open identity overview' },
}
const summary = computed(() => summaries[status.value])
async function loadStatus() {
  status.value = 'loading'
  try {
    const result = await getVerificationStatus()
    const key = result?.status || result?.decision?.finalDecision
    status.value = ['not_started','pending','review','verified','rejected'].includes(key) ? key : 'unavailable'
  } catch {
    status.value = 'unavailable'
  }
}
onMounted(loadStatus)
</script>
<style scoped>
.identity-summary { border:1px solid #384364; border-radius:12px; background:#1b233c; color:#f4f6ff; padding:clamp(24px,4vw,48px); }
.summary-label { display:flex; align-items:center; gap:10px; margin-bottom:24px; color:#c3cdff; font-size:14px; }
#app .identity-summary h2 { font-size:clamp(28px,3vw,42px); letter-spacing:-.05em; color:inherit; font-weight:550; }
.identity-summary p { color:#ccd2e7; margin-top:8px; max-width:55ch; }
.summary-actions { display:flex; gap:12px; margin-top:24px; flex-wrap:wrap; }
.summary-actions a,.summary-actions button { display:inline-flex; gap:14px; align-items:center; padding:10px 16px; border-radius:7px; font-size:14px; min-height:44px; }
.summary-actions a { background:#c4cdff; color:#171e36; font-weight:550; text-decoration:none; }
.summary-actions a:hover { background:#d7ddff; }
.summary-actions button { background:transparent; color:white; border:1px solid #8b97be; }
.workspace-tools { margin-top:20px; display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.workspace-tools a { display:flex; align-items:center; gap:16px; padding:24px; border:1px solid var(--line); border-radius:10px; text-decoration:none; color:var(--ink); background:var(--surface); }
.workspace-tools a:hover { border-color:var(--selected-border); }
.workspace-tools svg { flex:none; color:var(--link); }
.workspace-tools svg:last-child { margin-left:auto; }
.workspace-tools p { font-size:14px; color:var(--muted); margin-top:4px; }
@media(max-width:960px) { .workspace-tools { grid-template-columns:1fr; } }
@media(max-width:500px) { .workspace-tools a { padding:16px; gap:12px; } }
</style>
