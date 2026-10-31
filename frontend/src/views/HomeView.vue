<template>
  <div ref="pageRoot" class="landing" :class="{ 'motion-ready': motionReady, 'motion-paused': !playing }">
    <a href="#main-content" class="landing-skip">Skip to content</a>
    <header class="site-header">
      <div class="nav-wrap">
        <RouterLink to="/" class="wordmark" aria-label="Verity home"><span class="logo-symbol"><ShieldCheck :size="23" /></span>verity<span class="logo-period">.</span></RouterLink>
        <nav class="desktop-nav" aria-label="Main navigation"><a href="#how-it-works" @click.prevent="goTo('how-it-works')">How it works</a><a href="#why-verity" @click.prevent="goTo('why-verity')">Why Verity</a><a href="#questions" @click.prevent="goTo('questions')">FAQs</a></nav>
        <div class="nav-actions"><RouterLink to="/login" class="signin-link">Sign in <ArrowUpRight :size="16" /></RouterLink><RouterLink to="/register" class="button button-small">Register now <ArrowRight :size="16" /></RouterLink></div>
        <button class="menu-button" :aria-expanded="menuOpen" aria-controls="mobile-navigation" :aria-label="menuOpen ? 'Close navigation' : 'Open navigation'" @click="menuOpen = !menuOpen"><X v-if="menuOpen" :size="24" /><Menu v-else :size="24" /></button>
      </div>
      <nav v-if="menuOpen" id="mobile-navigation" class="mobile-nav" aria-label="Mobile navigation"><a href="#how-it-works" @click.prevent="goTo('how-it-works')">How it works <ArrowUpRight :size="16" /></a><a href="#why-verity" @click.prevent="goTo('why-verity')">Why Verity <ArrowUpRight :size="16" /></a><a href="#questions" @click.prevent="goTo('questions')">FAQs <ArrowUpRight :size="16" /></a><RouterLink to="/login">Sign in <ArrowRight :size="16" /></RouterLink><RouterLink to="/register">Register now <ArrowRight :size="16" /></RouterLink></nav>
    </header>
    <main id="main-content">
      <section class="hero section-wrap">
        <div class="hero-copy">
          <p class="eyebrow hero-eyebrow"><span class="status-dot" /> A MORE HUMAN WAY TO VERIFY</p>
          <h1>Trust starts<br />with the<br /><em>real you.</em><span class="title-spark" aria-hidden="true">✳</span></h1>
          <p class="hero-description">Your next chapter starts with a trusted identity. Register, verify your documents, and take a live selfie—all in one guided workspace.</p>
          <div class="hero-actions"><RouterLink to="/register" class="button">Register now <ArrowUpRight :size="20" /></RouterLink><a href="#how-it-works" class="text-button" @click.prevent="goTo('how-it-works')"><span class="play-circle"><Play :size="12" fill="currentColor" /></span>See how it works</a></div>
          <div class="hero-note"><ShieldCheck :size="16" /><span>Your documents. Your identity. A clearer way forward.</span></div>
        </div>
        <div class="hero-visual" aria-label="Illustration of the Verity verification process">
          <div class="visual-grid" aria-hidden="true" /><div class="orbit orbit-one" aria-hidden="true" /><div class="orbit orbit-two" aria-hidden="true" /><span class="orbit-point" aria-hidden="true" />
          <div class="visual-caption"><span>THE VERITY CHECK</span><span>01 — 03</span></div>
          <div class="identity-card">
            <div class="identity-top"><span><ShieldCheck :size="17" /> VERITY ID</span><span class="card-chip"><i /><i /><i /></span></div>
            <div class="portrait-area">
              <svg class="portrait-art" viewBox="0 0 260 240" fill="none" aria-hidden="true">
                <defs><linearGradient id="portrait-bg" x1="0" y1="0" x2="260" y2="240" gradientUnits="userSpaceOnUse"><stop stop-color="#d1ddc9" /><stop offset="1" stop-color="#a6c0af" /></linearGradient><linearGradient id="portrait-coat" x1="70" y1="150" x2="200" y2="240" gradientUnits="userSpaceOnUse"><stop stop-color="#2b6a60" /><stop offset="1" stop-color="#17473e" /></linearGradient></defs>
                <rect width="260" height="240" rx="16" fill="url(#portrait-bg)" /><circle cx="130" cy="110" r="88" stroke="#f3f4e9" stroke-opacity=".45" /><circle cx="130" cy="110" r="68" stroke="#f3f4e9" stroke-opacity=".35" />
                <path d="M44 240c1-48 29-79 86-79s85 31 86 79" fill="url(#portrait-coat)" /><path d="M107 146h46v29c-11 20-35 20-46 0z" fill="#ba8067" /><path d="M88 91c0-39 84-43 84 0v31c0 35-22 52-42 52s-42-17-42-52z" fill="#d7a185" />
                <path d="M84 105c-10-29-1-62 31-68 27-5 56 4 64 29 5 16 1 30-8 42l-4-24c-14 2-32-5-43-16-9 17-23 23-36 23z" fill="#253e36" /><path d="M113 128c10 6 24 6 34 0" stroke="#a46756" stroke-width="2.5" stroke-linecap="round" /><path d="m92 191 38 28 38-28" stroke="#528276" stroke-width="1.5" />
                <path v-if="demoStep === 1" d="M106 91 94 112l9 31 27 15 27-15 9-31-12-21-24-10zM94 112h72M103 143l27-62 27 62M106 91l51 52m-3-52-51 52" stroke="#f2ffc7" stroke-width="1" opacity=".8" />
              </svg>
              <div class="scan-corners" aria-hidden="true"><i /><i /><i /><i /></div><div v-if="demoStep !== 2" class="scan-line" aria-hidden="true" /><span class="portrait-label">ILLUSTRATIVE PROFILE</span>
            </div>
            <div class="identity-details"><div><span class="micro-label">IDENTITY WORKSPACE</span><strong>A trusted beginning.</strong></div><Fingerprint :size="35" :stroke-width="1.2" /></div>
            <div class="identity-bottom"><span v-for="n in 28" :key="n" :style="{ height: `${10 + (n * 7) % 15}px`, width: n % 3 ? '2px' : '4px' }" /><small>VERITY / YOUR NEXT CHAPTER</small></div>
          </div>
          <Transition name="badge" mode="out-in"><div :key="demoStep" class="floating-badge"><span class="badge-icon"><component :is="demoSteps[demoStep].icon" :size="21" /></span><div><span>{{ demoSteps[demoStep].eyebrow }}</span><strong>{{ demoSteps[demoStep].label }}</strong></div><span class="badge-dot" /></div></Transition>
          <div class="floating-note"><span class="note-stars">✦ ✦ ✦</span><span>Built around<br /><strong>the real you.</strong></span></div>
          <div class="demo-controls"><div class="demo-tabs" role="group" aria-label="Explore verification steps"><button v-for="(step, index) in demoSteps" :key="step.label" :aria-pressed="demoStep === index" @click="selectDemo(index)"><span>0{{ index + 1 }}</span>{{ step.short }}</button></div><button class="pause-button" :aria-label="playing ? 'Pause illustration animation' : 'Play illustration animation'" @click="playing = !playing"><Pause v-if="playing" :size="15" /><Play v-else :size="15" /></button></div>
          <p class="demo-disclaimer">A preview of the journey. Your verification happens after registration.</p>
        </div>
      </section>
      <div class="document-strip"><div class="section-wrap strip-inner"><p>ONE WORKSPACE.<br /><strong>YOUR WAY IN.</strong></p><span><ContactRound :size="22" :stroke-width="1.4" />National ID</span><span><BookOpen :size="22" :stroke-width="1.4" />Passport</span><span><IdCard :size="22" :stroke-width="1.4" />Driver’s licence</span><span class="strip-selfie"><ScanFace :size="22" :stroke-width="1.4" />Live selfie</span></div></div>
      <section id="how-it-works" class="journey section-wrap section-space">
        <div class="section-heading reveal"><div><p class="eyebrow">LESS GUESSWORK. MORE GUIDANCE.</p><h2>A clear path.<br /><em>Every step of the way.</em></h2></div><p>No wondering what comes next. We guide you from your first details to your verification result.</p></div>
        <div class="steps-grid"><article v-for="(step, index) in journeySteps" :key="step.title" class="journey-step reveal" :style="{ '--reveal-delay': `${index * 100}ms` }"><div class="step-top"><span class="step-number">0{{ index + 1 }}</span><component :is="step.icon" :size="30" :stroke-width="1.25" /></div><h3>{{ step.title }}</h3><p>{{ step.description }}</p><span class="step-footnote"><span />{{ step.note }}</span></article></div>
      </section>
      <section id="why-verity" class="why-section"><div class="section-wrap why-inner">
        <div class="why-copy reveal"><p class="eyebrow">THOUGHTFUL CHECKS. HUMAN EXPERIENCE.</p><h2>More than a photo.<br /><em>A fuller picture.</em></h2><p class="why-intro">One image never tells the whole story. Verity brings document, face, and liveness checks together in a single verification journey.</p><a href="#questions" class="why-link" @click.prevent="goTo('questions')">Get to know the process <ArrowUpRight :size="19" /></a><div class="trust-art" aria-hidden="true"><div class="trust-ring" /><div class="trust-ring second" /><Fingerprint class="trust-fingerprint" :size="82" :stroke-width=".8" /><span class="trust-tag trust-tag-one"><ScanFace :size="14" /> Face matching</span><span class="trust-tag trust-tag-two"><ShieldCheck :size="14" /> Document checks</span><span class="trust-center-dot" /></div></div>
        <div class="feature-list"><article v-for="(feature, index) in features" :key="feature.title" class="feature-row reveal" :style="{ '--reveal-delay': `${index * 80}ms` }"><span class="feature-icon"><component :is="feature.icon" :size="23" :stroke-width="1.5" /></span><div><h3>{{ feature.title }}</h3><p>{{ feature.description }}</p></div><span class="feature-index">0{{ index + 1 }}</span></article></div>
      </div></section>
      <section id="questions" class="faq-section section-wrap section-space"><div class="faq-heading reveal"><p class="eyebrow">BEFORE YOU BEGIN</p><h2>A little clarity<br /><em>goes a long way.</em></h2><p>Good questions. Straightforward answers.</p><span class="faq-doodle" aria-hidden="true">↳</span></div><div class="faq-list reveal"><details v-for="(faq, index) in faqs" :key="faq.question" :open="index === 0"><summary>{{ faq.question }}<Plus :size="19" aria-hidden="true" /></summary><div class="faq-answer"><p>{{ faq.answer }}</p></div></details></div></section>
      <section class="cta-section section-wrap reveal"><div class="cta-panel"><span class="cta-orbit" aria-hidden="true" /><div class="cta-copy"><p class="eyebrow">YOUR NEXT CHAPTER STARTS HERE</p><h2>Let’s make it<br /><em>officially you.</em></h2><p>A trusted beginning is just a few steps away.</p><div class="cta-actions"><RouterLink to="/register" class="button">Register now <ArrowUpRight :size="20" /></RouterLink><RouterLink to="/login" class="text-button">Already registered? Sign in <ArrowRight :size="18" /></RouterLink></div></div><div class="cta-seal" aria-hidden="true"><span>YOUR IDENTITY</span><ShieldCheck :size="78" :stroke-width="1" /><span>NEW POSSIBILITIES</span></div></div></section>
    </main>
    <footer class="site-footer section-wrap"><div class="footer-top"><RouterLink to="/" class="wordmark"><span class="logo-symbol"><ShieldCheck :size="23" /></span>verity<span class="logo-period">.</span></RouterLink><p>A trusted beginning.<br />A more human connection.</p><nav aria-label="Footer navigation"><a href="#how-it-works" @click.prevent="goTo('how-it-works')">How it works</a><RouterLink to="/register">Register</RouterLink><RouterLink to="/login">Sign in</RouterLink></nav></div><div class="footer-bottom"><span>© {{ new Date().getFullYear() }} Verity. Identity, thoughtfully verified.</span><span>Intelligent Agent Identity Verification System</span><button @click="backToTop">Back to top <ArrowUpRight :size="14" /></button></div></footer>
  </div>
</template>
<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { ArrowRight, ArrowUpRight, ShieldCheck, Fingerprint, ScanFace, ContactRound, BookOpen, IdCard, Check, Menu, X, Play, Pause, Plus, UserRound, ScanLine, ListChecks, KeyRound } from '@lucide/vue'
const pageRoot = ref(null), menuOpen = ref(false), motionReady = ref(false), playing = ref(false), demoStep = ref(0)
const demoSteps = [
  { short:'Document', eyebrow:'01 / DOCUMENT', label:'Details come into focus', icon:ScanLine },
  { short:'Selfie', eyebrow:'02 / LIVE SELFIE', label:'A moment of movement', icon:ScanFace },
  { short:'Review', eyebrow:'03 / YOUR RESULT', label:'Clarity on what’s next', icon:Check },
]
const journeySteps = [
  { title:'Start with your details.', icon:UserRound, description:'Create your account and confirm your personal information. Your workspace keeps the next step in view.', note:'A place to begin' },
  { title:'Bring your identity to life.', icon:ScanFace, description:'Provide your identity document, then take a centred selfie and follow a left or right head-turn prompt.', note:'Guided, not complicated' },
  { title:'Know where you stand.', icon:ListChecks, description:'Follow the checks and view your result in your dashboard, with guidance when another step is needed.', note:'A clear next step' },
]
const features = [
  { title:'A clearer document, from the start.', icon:ScanLine, description:'Image-quality checks help you capture readable details before your document moves through verification.' },
  { title:'Your face. A live moment.', icon:ScanFace, description:'Face matching and liveness checks accompany a guided selfie, with a simple head turn to the left or right.' },
  { title:'A workspace that keeps you informed.', icon:ListChecks, description:'See your verification progress, review the outcome, and follow any available recapture instructions.' },
  { title:'A familiar way back in.', icon:KeyRound, description:'Sign in with email or Google. On supported devices, add a passkey for your next visit.' },
]
const faqs = [
  { question:'What do I need to get started?', answer:'Have your personal details, an accepted identity document, and a device with a working camera ready. You will also need access to your email to complete account registration.' },
  { question:'Which identity documents can I use?', answer:'Verity supports a national ID, passport, or driver’s licence. For a national ID, you will be guided through the front and back. For a passport, use the bio-data page; for a licence, use the front.' },
  { question:'What happens during the live selfie check?', answer:'First, centre your face for a clear photo. Then follow the instruction to turn your head left or right. Allow camera access and use a well-lit space so the face tracker can follow your movement.' },
  { question:'What if my verification needs another attempt?', answer:'Your dashboard shows the result and any available next steps. If a document retry is available, you must take fresh camera photos rather than upload saved files. Some outcomes may require further review.' },
  { question:'Can I use my phone?', answer:'Yes. Use a current browser, allow camera access, and keep your document nearby. You can register, take your photos, and check your status from the same device.' },
]
let observer, timer, motionPreference, originalTitle
function goTo(id) { menuOpen.value = false; document.getElementById(id)?.scrollIntoView({ behavior:motionPreference?.matches ? 'auto' : 'smooth', block:'start' }) }
function backToTop() { window.scrollTo({ top:0, behavior:motionPreference?.matches ? 'auto' : 'smooth' }) }
function selectDemo(index) { demoStep.value = index; playing.value = false }
function updateMotion() { playing.value = !motionPreference.matches }
function closeMenu(event) { if (event.key === 'Escape') menuOpen.value = false }
onMounted(() => {
  originalTitle = document.title
  document.title = 'Verity — A trusted beginning. A more human connection.'
  motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)')
  updateMotion(); motionPreference.addEventListener('change', updateMotion)
  if ('IntersectionObserver' in window) {
    observer = new IntersectionObserver(entries => entries.forEach(entry => { if (entry.isIntersecting) { entry.target.classList.add('is-visible'); observer.unobserve(entry.target) } }), { threshold:0.08 })
    pageRoot.value.querySelectorAll('.reveal').forEach(el => observer.observe(el)); motionReady.value = true
  }
  timer = window.setInterval(() => { if (playing.value && !document.hidden) demoStep.value = (demoStep.value + 1) % demoSteps.length }, 4500)
  window.addEventListener('keydown', closeMenu)
})
onBeforeUnmount(() => { observer?.disconnect(); window.clearInterval(timer); motionPreference?.removeEventListener('change', updateMotion); window.removeEventListener('keydown', closeMenu); document.title = originalTitle })
</script>
<style scoped src="../landing.css"></style>
