<template>
  <div class="landing">
    <a class="landing-skip" href="#main-content">Skip to content</a>
    <header class="site-header">
      <div class="wrap nav-wrap">
        <RouterLink to="/" class="wordmark" aria-label="Verity home"><img src="/verity.svg" alt="" />Verity</RouterLink>
        <nav class="desktop-nav" aria-label="Main navigation">
          <a v-for="link in sections" :key="link.id" :href="'#' + link.id">{{ link.label }}</a>
        </nav>
        <div class="nav-actions">
          <RouterLink to="/login">Sign in</RouterLink>
          <RouterLink to="/register" class="button compact">Create account <ArrowUpRight :size="16" /></RouterLink>
        </div>
        <button ref="menuTrigger" class="menu-button" :aria-expanded="menuOpen" aria-controls="mobile-navigation" :aria-label="menuOpen ? 'Close navigation' : 'Open navigation'" @click="menuOpen = !menuOpen">
          <X v-if="menuOpen" /><Menu v-else />
        </button>
      </div>
      <nav v-if="menuOpen" id="mobile-navigation" class="mobile-nav wrap" aria-label="Mobile navigation">
        <a v-for="link in sections" :key="link.id" :href="'#' + link.id" @click="menuOpen = false">{{ link.label }} <ArrowRight :size="16" /></a>
        <RouterLink to="/login">Sign in <ArrowRight :size="16" /></RouterLink>
        <RouterLink to="/register">Create account <ArrowUpRight :size="16" /></RouterLink>
      </nav>
    </header>

    <main id="main-content">
      <section class="hero wrap" aria-labelledby="hero-title">
        <div class="hero-copy">
          <p class="kicker"><span class="registration-mark" aria-hidden="true"></span> Agent registration</p>
          <h1 id="hero-title">Verify your<br /><span>identity.</span></h1>
          <p class="hero-description">Verify your identity with a photo ID and a guided live selfie. Follow each check from your own agent workspace.</p>
          <div class="hero-actions"><RouterLink class="button" to="/register">Start verification <ArrowUpRight :size="19" /></RouterLink><a class="secondary-link" href="#how-it-works">How it works <ArrowDown :size="16" /></a></div>
        </div>
        <figure class="study">
          <img class="study-image" src="/fingerprint-study.webp" width="1080" height="1080" alt="A sculpted fingerprint with finely cut metal ridges" fetchpriority="high" />
          <div class="study-frame" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
          <figcaption><span><Fingerprint :size="16" /> Fingerprint study</span><span>Fig. 01</span></figcaption>
        </figure>
      </section>
      <section class="document-strip" aria-label="Accepted identity documents">
        <div class="wrap strip-inner"><p>Accepted documents</p><span><ContactRound />National ID</span><span><BookOpen />Passport</span><span><IdCard />Driver’s licence</span></div>
      </section>

      <section id="how-it-works" class="wrap section-space journey">
        <div class="section-heading"><h2>How verification works</h2><p>Register and confirm your personal details. Then follow these three checks in your workspace.</p></div>
        <div class="process-grid">
          <div class="demo-tabs" role="group" aria-label="Explore verification steps">
            <button v-for="(step, index) in steps" :key="step.short" aria-controls="verification-preview" :aria-pressed="demoStep === index" @click="selectStep(index)">
              <span class="step-index" aria-hidden="true">0{{ index + 1 }}</span><span>{{ step.short }}</span><ArrowUpRight :size="18" />
            </button>
          </div>
          <div id="verification-preview" class="process-preview">
            <div class="preview-header"><span>Verification preview</span><button :aria-label="playing ? 'Pause verification preview' : 'Play verification preview'" @click="togglePlayback"><Pause v-if="playing" :size="16" /><Play v-else :size="16" /></button></div>
            <div class="preview-body">
              <div class="preview-symbol" aria-hidden="true"><component :is="steps[demoStep].icon" :size="76" :stroke-width="1.1" /></div>
              <div><h3>{{ steps[demoStep].title }}</h3><p>{{ steps[demoStep].detail }}</p></div>
            </div>
          </div>
        </div>
      </section>

      <section id="why-verity" class="checks-section">
        <div class="wrap checks-inner">
          <div class="checks-title"><p class="kicker"><span class="registration-mark" aria-hidden="true"></span> Inside Verity</p><h2>Behind <br />the checks</h2></div>
          <div class="feature-list">
            <article v-for="feature in features" :key="feature.title"><component :is="feature.icon" :size="24" :stroke-width="1.5" /><div><h3>{{ feature.title }}</h3><p>{{ feature.description }}</p></div></article>
          </div>
        </div>
      </section>

      <section id="questions" class="wrap section-space faq-section">
        <div><h2>Before you begin</h2><p class="section-subtitle">Documents, camera access, and next steps.</p></div>
        <div class="faq-list"><details v-for="(faq, index) in faqs" :key="faq.question" :open="index === 0">
          <summary>{{ faq.question }}<Plus :size="18" /></summary><p>{{ faq.answer }}</p>
        </details></div>
      </section>
      <section class="cta-section"><div class="wrap cta-inner"><h2>Ready to verify?</h2><RouterLink class="button" to="/register">Create your account <ArrowUpRight :size="18" /></RouterLink></div></section>
    </main>
    <footer class="site-footer wrap"><RouterLink to="/" class="wordmark" aria-label="Verity home"><img src="/verity.svg" alt="" />Verity</RouterLink><span>© {{ new Date().getFullYear() }} Verity</span><nav aria-label="Footer navigation"><a href="#questions">FAQs</a><RouterLink to="/login">Sign in</RouterLink><a href="#main-content">Back to top <ArrowUp :size="15" /></a></nav></footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { ArrowDown, ArrowRight, ArrowUp, ArrowUpRight, BookOpen, ContactRound, Fingerprint, IdCard, KeyRound, ListChecks, Menu, Pause, Play, Plus, ScanFace, ScanLine, X } from '@lucide/vue'

const sections = [
  { id: 'how-it-works', label: 'How it works' },
  { id: 'why-verity', label: 'Why Verity' },
  { id: 'questions', label: 'FAQs' },
]
const steps = [
  { short: 'Document', title: 'Capture your photo ID', detail: 'Choose your document type and follow the prompts to capture each required side.', icon: ContactRound },
  { short: 'Selfie', title: 'Take a live selfie', detail: 'Centre your face in the camera, then turn your head in the direction shown on screen.', icon: ScanFace },
  { short: 'Review', title: 'Check your result', detail: 'Open your dashboard to see your verification status and any instructions for another attempt.', icon: ListChecks },
]
const features = [
  { title: 'Document quality', description: 'Image checks help you capture readable details before submission.', icon: ScanLine },
  { title: 'Face matching and liveness', description: 'Verity compares your selfie with your document portrait and checks your guided head movement.', icon: ScanFace },
  { title: 'Verification history', description: 'Your dashboard shows the outcome. Your activity history keeps a record of account actions.', icon: ListChecks },
  { title: 'Passkey sign-in', description: 'Add a passkey on a supported device to sign in again. Email and Google sign-in are also available.', icon: KeyRound },
]
const faqs = [
  { question: 'What do I need to get started?', answer: 'Have your personal details, an accepted photo ID, and a device with a working camera ready. You also need access to your email to confirm your account.' },
  { question: 'Which identity documents can I use?', answer: 'Use the front and back of a national ID, the photo page of a passport, or the front of a driver’s licence.' },
  { question: 'What happens during the live selfie check?', answer: 'Allow camera access and face a light source. Centre your face for a photo, then follow the prompt to turn your head left or right.' },
  { question: 'What if I need another attempt?', answer: 'Your dashboard shows your next steps. When a document retry is available, take fresh photos with your camera. Some submissions need further review.' },
  { question: 'Can I use my phone?', answer: 'Yes. Use a current browser with camera access to register, take photos, and check your status on the same device.' },
]
const menuOpen = ref(false)
const menuTrigger = ref(null)
const demoStep = ref(0)
const playing = ref(false)
let timer
let motionPreference
let originalTitle

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
  originalTitle = document.title
  document.title = 'Verity — Agent identity verification'
  motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)')
  motionPreference.addEventListener('change', stopPlayback)
  window.addEventListener('keydown', closeMenu)
})
onBeforeUnmount(() => {
  stopPlayback()
  motionPreference?.removeEventListener('change', stopPlayback)
  window.removeEventListener('keydown', closeMenu)
  document.title = originalTitle
})
</script>

<style scoped src="../landing.css"></style>
