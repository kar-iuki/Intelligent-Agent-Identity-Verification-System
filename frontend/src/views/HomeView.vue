<template>
  <div class="landing">
    <a class="skip" href="#main-content">Skip to content</a>
    <header class="site-header">
      <div class="wrap nav-wrap">
        <RouterLink to="/" class="wordmark" aria-label="Verity home"><img src="/verity.svg" alt="" />Verity</RouterLink>
        <nav class="desktop-nav" aria-label="Main navigation"><a href="#how-it-works">How it works</a><a href="#guide">Document guide</a><a href="#questions">Help</a></nav>
        <RouterLink class="sign-in" to="/login">Sign in <ArrowUpRight :size="16" /></RouterLink>
        <button ref="menuTrigger" class="menu-button" :aria-expanded="menuOpen" aria-controls="mobile-navigation" :aria-label="menuOpen ? 'Close navigation' : 'Open navigation'" @click="menuOpen = !menuOpen"><X v-if="menuOpen" /><Menu v-else /></button>
      </div>
      <nav v-if="menuOpen" id="mobile-navigation" class="mobile-nav wrap" aria-label="Mobile navigation">
        <a href="#how-it-works" @click="menuOpen = false">How it works</a><a href="#guide" @click="menuOpen = false">Document guide</a><a href="#questions" @click="menuOpen = false">Help</a>
      </nav>
    </header>
    <main id="main-content">
      <section class="intro" aria-labelledby="hero-title">
        <div class="wrap hero">
          <div class="hero-copy">
            <p class="hero-context"><ScanFace :size="18" aria-hidden="true" />Agent identity verification</p>
            <h1 id="hero-title">Your identity,<br /><span>in focus.</span></h1>
            <p class="hero-description">Verify your identity with a photo ID and a live selfie. Follow each check from your agent workspace.</p>
            <div class="hero-actions"><RouterLink class="start" to="/register">Create an account <ArrowRight :size="19" /></RouterLink><a href="#guide">Try a sample <ArrowDown :size="16" /></a></div>
          </div>
          <figure class="print-study">
            <img src="/fingerprint-study.webp" alt="A sculpted fingerprint formed from brushed silver ridges" width="1080" height="1080" fetchpriority="high" />
            <div class="study-frame" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
          </figure>
        </div>
        <div class="prep-strip">
          <div class="wrap prep-inner">
            <span>What you’ll need</span>
            <ul>
              <li><ContactRound aria-hidden="true" />Photo ID</li>
              <li><Camera aria-hidden="true" />Camera</li>
              <li><Mail aria-hidden="true" />Email access</li>
            </ul>
          </div>
        </div>
      </section>

      <section id="guide" class="wrap guide-layout" aria-labelledby="guide-title">
        <div class="guide-intro section-title">
          <h2 id="guide-title">Document guide</h2>
          <p>Try a capture with a sample document before using your own. Choose an ID and check how it looks in the frame.</p>
          <p class="camera-note"><CameraOff :size="16" aria-hidden="true" /> Your camera stays off during practice</p>
        </div>
        <div ref="practiceRoot" class="practice-mount"></div>
      </section>

      <section id="how-it-works" class="wrap flow-section">
        <div class="section-title"><h2>How verification works</h2><p>Start with your email, then complete these checks.</p></div>
        <div class="step-selector" role="group" aria-label="Explore verification steps">
          <button v-for="(step, index) in steps" :key="step.short" :aria-pressed="demoStep === index" aria-controls="verification-preview" @click="selectStep(index)">
            <span class="step-number" aria-hidden="true">0{{ index + 1 }}</span><span>{{ step.short }}</span><component :is="step.icon" :size="22" aria-hidden="true" />
          </button>
        </div>
        <div id="verification-preview" class="instruction-row"><div><h3>{{ steps[demoStep].title }}</h3><p>{{ steps[demoStep].detail }}</p></div><button class="play" @click="togglePlayback" :aria-label="playing ? 'Pause verification preview' : 'Play verification preview'"><Pause v-if="playing" :size="16" /><Play v-else :size="16" /></button></div>
      </section>

      <section id="questions" class="help-section">
        <div class="wrap help-layout"><div class="section-title"><h2>Before you start</h2><p>Answers to common verification questions.</p></div>
          <div class="faq-list"><details v-for="faq in faqs" :key="faq.question"><summary>{{ faq.question }}<Plus :size="18" /></summary><p>{{ faq.answer }}</p></details></div>
        </div>
      </section>
    </main>
    <footer class="site-footer wrap"><RouterLink class="wordmark" to="/" aria-label="Verity home"><img src="/verity.svg" alt="" />Verity</RouterLink><span>Agent identity verification</span><nav aria-label="Footer navigation"><RouterLink to="/register">Create account</RouterLink><RouterLink to="/login">Sign in</RouterLink></nav></footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { ArrowDown, ArrowRight, ArrowUpRight, Camera, CameraOff, ContactRound, ListChecks, Mail, Menu, Pause, Play, Plus, ScanFace, X } from '@lucide/vue'

import { mountCapturePractice } from '../components/capturePractice.js'
import '../capture.css'

const practiceRoot = ref(null)
let disposePractice
const steps = [
  { short:'Document', title:'Capture your photo ID', detail:'Choose a national ID, passport, or driver’s licence. Follow the capture prompts and check that the details are readable.', icon:ContactRound },
  { short:'Selfie', title:'Take a live selfie', detail:'Face the camera in good light. Take a centred photo, then turn your head in the direction shown.', icon:ScanFace },
  { short:'Review', title:'Check your result', detail:'Open your identity overview to see the decision, review any feedback, or complete a requested retry.', icon:ListChecks },
]
const faqs = [
  { question:'What do I need to get started?', answer:'Have your email, personal details, photo ID, and a camera-enabled phone or computer ready. Verity sends a confirmation link to your email when you register.' },
  { question:'Which identity documents can I use?', answer:'Use the front and back of a national ID, the photo page of a passport, or the front of a driver’s licence.' },
  { question:'How does the live selfie check work?', answer:'Verity compares your selfie with your document portrait. A guided head turn checks for movement. Allow camera access when you reach the selfie step.' },
  { question:'What happens if I need to try again?', answer:'Your identity overview shows the next step. If a document retry is available, use the camera to take fresh photos. Some cases go to an administrator for review.' },
  { question:'How do I return to my workspace?', answer:'Sign in with email or Google. On a supported device, you can also use a passkey you have registered. Your workspace includes your verification status and account activity.' },
]
const menuOpen = ref(false)
const menuTrigger = ref(null)
const demoStep = ref(0)
const playing = ref(false)
let timer, motionPreference, originalTitle
function stopPlayback() {
  clearInterval(timer)
  playing.value = false
}
function togglePlayback() {
  if (playing.value) return stopPlayback()
  playing.value = true
  timer = window.setInterval(() => {
    if (!document.hidden) demoStep.value = (demoStep.value + 1) % steps.length
  }, 5500)
}
function selectStep(index) {
  stopPlayback()
  demoStep.value = index
}
function closeMenu(event) {
  if (event.key === 'Escape' && menuOpen.value) {
    menuOpen.value = false
    menuTrigger.value?.focus()
  }
}
onMounted(() => {
  disposePractice = mountCapturePractice(practiceRoot.value)
  originalTitle = document.title
  document.title = 'Verity — Agent identity verification'
  motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)')
  motionPreference.addEventListener('change', stopPlayback)
  window.addEventListener('keydown', closeMenu)
})
onBeforeUnmount(() => {
  disposePractice?.()
  stopPlayback()
  motionPreference?.removeEventListener('change', stopPlayback)
  window.removeEventListener('keydown', closeMenu)
  document.title = originalTitle
})
</script>

<style scoped src="../landing.css"></style>
