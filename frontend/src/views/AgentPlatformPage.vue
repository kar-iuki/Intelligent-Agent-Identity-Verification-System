<template>
  <div class="platform workspace">
    <header class="platform-header">
      <div>
        <p class="workspace-eyebrow">AGENT PORTAL / WORKSPACE</p>
        <h1>Agent Platform</h1>
        <p class="subtitle">Your identity, activity, and account security in one place.</p>
      </div>

    </header>

    <PasskeyPrompt :ready="true" />
    <main class="platform-content">
      <section class="card workspace-welcome">
        <p class="workspace-eyebrow">YOUR NEXT STEP</p>
        <h2>A workspace built around your identity</h2>
        <p>Keep your verification up to date, review your account activity, and manage how you sign in.</p>
      </section>
      <div class="platform-grid">
        <router-link class="platform-link" to="/agent/dashboard"><ShieldCheck :size="26" /><h2>Identity overview</h2><p>Follow your registration progress and check your verification status.</p><span>View your identity →</span></router-link>
        <router-link class="platform-link" to="/agent/audit"><History :size="26" /><h2>Activity history</h2><p>See a chronological record of actions and outcomes on your account.</p><span>Explore activity →</span></router-link>
        <router-link class="platform-link" to="/agent/passkeys"><Fingerprint :size="26" /><h2>Account security</h2><p>Add and manage passkeys for a simpler way to sign in with your device.</p><span>Manage passkeys →</span></router-link>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ShieldCheck, History, Fingerprint } from '@lucide/vue'
import PasskeyPrompt from '../components/PasskeyPrompt.vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'

const router = useRouter()
const { logout } = useAuthStore()

async function handleLogout() {
  await logout()
  router.push('/login')
}
</script>

<style scoped>
.platform {
  min-height: 100vh;
  background: #f0f4f8;
}

.platform-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 2rem;
  background: #fff;
  border-bottom: 1px solid #d9e2ec;
}

h1 {
  font-size: 1.25rem;
  color: #16213e;
}

.subtitle {
  color: #627d98;
  font-size: 0.875rem;
}

.actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.link {
  color: #3e7cb1;
  text-decoration: none;
  font-weight: 600;
}

.btn-logout {
  padding: 0.5rem 1rem;
  border: 1px solid #d9e2ec;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
}

.platform-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.card {
  background: #fff;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

h2 {
  margin-bottom: 0.75rem;
  color: #16213e;
}

p {
  color: #52606d;
  line-height: 1.6;
}
</style>
