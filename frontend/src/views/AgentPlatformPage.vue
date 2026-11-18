<template>
  <div class="platform workspace">
    <header><div><h1>My workspace</h1><p class="subtitle">Verification, activity, and sign-in settings for your account.</p></div></header>
    <PasskeyPrompt :ready="accountConfirmed" />
    <main class="platform-content">
      <RouterLink class="identity-entry" to="/agent/dashboard">
        <div><h2>Identity overview</h2><p>Check your verification status and continue any outstanding steps.</p><span>Open identity overview <ArrowRight :size="17" /></span></div>
        <img src="/fingerprint-study.webp" alt="" width="1080" height="1080" />
      </RouterLink>
      <div class="workspace-tools">
        <RouterLink to="/agent/audit"><History /><div><h2>Activity history</h2><p>Review account actions and their outcomes.</p></div><ArrowRight :size="18" /></RouterLink>
        <RouterLink to="/agent/passkeys"><Fingerprint /><div><h2>Passkeys &amp; security</h2><p>Manage the devices you use to sign in.</p></div><ArrowRight :size="18" /></RouterLink>
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ArrowRight, History, Fingerprint } from '@lucide/vue'
import PasskeyPrompt from '../components/PasskeyPrompt.vue'
import { getVerificationStatus } from '../services/verificationService.js'

const accountConfirmed = ref(false)

onMounted(async () => {
  try {
    const status = await getVerificationStatus()
    accountConfirmed.value = status?.status === 'verified' || status?.decision?.finalDecision === 'verified'
  } catch {
    accountConfirmed.value = false
  }
})
</script>

<style scoped>
.identity-entry { display:flex; align-items:stretch; justify-content:space-between; overflow:hidden; background:#172820; color:#f1f4eb; text-decoration:none; border-radius:6px; }
.identity-entry > div { align-self:center; padding:clamp(24px,4vw,56px); }
#app .identity-entry h2 { color:inherit; font-size:clamp(28px,3.4vw,48px); font-weight:500; letter-spacing:-.055em; }
.identity-entry p { max-width:36ch; margin-block:12px 24px; color:#c8d6ca; }
.identity-entry span { display:inline-flex; align-items:center; gap:12px; font-size:14px; border-bottom:1px solid #83998a; padding-bottom:4px; }
.identity-entry img { width:35%; height:auto; max-height:320px; object-fit:cover; }
.identity-entry:hover span { border-color:currentColor; }
.workspace-tools { margin-top:28px; border-top:1px solid var(--line); }
.workspace-tools a { display:flex; align-items:center; gap:20px; padding:24px 12px; border-bottom:1px solid var(--line); text-decoration:none; color:var(--ink); }
.workspace-tools a:hover { background:var(--surface-hover); }
.workspace-tools a > svg { flex-shrink:0; }
.workspace-tools a > svg:last-child { margin-left:auto; }
.workspace-tools p { font-size:14px; color:var(--muted); margin-top:4px; }
@media(max-width:540px) { .identity-entry img { width:25%; } .identity-entry > div { padding:20px; } .workspace-tools a { gap:12px; padding:20px 4px; } }
</style>
