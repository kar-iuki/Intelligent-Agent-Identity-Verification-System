<template>
  <div class="auth-shell">
    <aside class="auth-story">
      <router-link to="/login" class="brand"><span class="brand-mark"><ShieldCheck :size="24" /></span><span>Verity<span class="brand-caption">IDENTITY WORKSPACE</span></span></router-link>
      <div class="auth-story-content"><span class="story-eyebrow">CONFIDENCE IN EVERY CONNECTION</span><h2>Your identity.<br />A trusted beginning.</h2><p>A clear path from registration to verification. Built around you, every step of the way.</p>
        <div class="identity-art" aria-hidden="true"><div class="art-orbit"></div><div class="art-id"><div class="art-id-top"><ShieldCheck :size="22" /><span>VERITY / IDENTITY</span></div><div class="art-person"><UserRound :size="32" /><div><i></i><i></i></div></div><div class="art-id-bottom"><span>ONE IDENTITY. NEW POSSIBILITIES.</span><Fingerprint :size="32" /></div></div><div class="art-verified"><CircleCheck :size="18" />Made for a trusted connection</div></div>
        <div class="story-features"><span><Fingerprint :size="18" />Simple sign-in</span><span><ShieldCheck :size="18" />Identity verification</span></div>
      </div><p class="auth-story-footer">Intelligent Agent Identity Verification System</p>
    </aside>
    <div class="auth-form-area"><slot /><footer>Verity · Your identity workspace</footer></div>
  </div>
</template>
<script setup>
import { ShieldCheck, Fingerprint, UserRound, CircleCheck } from '@lucide/vue'
</script>
