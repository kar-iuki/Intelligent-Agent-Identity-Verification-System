<template>
  <div class="auth-shell">
    <aside class="auth-story">
      <RouterLink to="/" class="brand" aria-label="Verity home">
        <img class="verity-mark" src="/verity.svg" alt="" />Verity
      </RouterLink>
      <div class="auth-story-content">
        <h2>Your identity<br />workspace</h2>
        <p>Register, verify your photo ID, and keep track of your verification status.</p>
      </div>
      <figure class="auth-study">
        <img src="/fingerprint-study.webp" alt="" width="1080" height="1080" />
        <figcaption><span>Fingerprint study</span><span>Fig. 01</span></figcaption>
      </figure>
    </aside>
    <div class="auth-form-area"><slot /></div>
  </div>
</template>
