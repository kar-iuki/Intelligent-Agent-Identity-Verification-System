<template>
  <div class="entry" :class="{ 'signin-entry': isSignIn }">
    <header class="entry-bar">
      <RouterLink to="/" class="entry-brand" aria-label="Verity home"><img src="/verity.svg" alt="" />Verity</RouterLink>
      <RouterLink to="/" class="return-home"><ArrowLeft :size="16" /> Back to home</RouterLink>
    </header>
    <div class="entry-layout" :class="{ 'with-guide': showGuide }">
      <div v-if="isSignIn" class="entry-study" aria-hidden="true">
        <img src="/fingerprint-study.webp" alt="" width="1080" height="1080" />
      </div>
      <main class="auth-shell"><div class="auth-form-area"><slot /></div></main>
      <aside v-if="showGuide" class="entry-guide">
        <div class="entry-art"><img src="/guide/national-id.webp" alt="" width="896" height="552" /></div>
        <div class="entry-checklist">
          <h2>What you’ll need</h2>
          <div><ContactRound /><p><strong>A photo ID</strong>National ID, passport, or driver’s licence.</p></div>
          <div><Camera /><p><strong>A working camera</strong>Use your phone or computer for the live selfie.</p></div>
          <div><Mail /><p><strong>Your email inbox</strong>Open the confirmation link to continue.</p></div>
        </div>
      </aside>
    </div>
  </div>
</template>
<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, Camera, ContactRound, Mail } from '@lucide/vue'
const route = useRoute()
const isSignIn = computed(() => route.name === 'login')
const showGuide = computed(() => route.name === 'register')
</script>
