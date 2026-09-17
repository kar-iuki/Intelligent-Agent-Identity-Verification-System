<template>
  <div class="platform">
    <header class="platform-header">
      <div>
        <h1>Agent Platform</h1>
        <p class="subtitle">Placeholder workspace for verified agents</p>
      </div>
      <div class="actions">
        <router-link class="link" to="/agent/dashboard">Back to dashboard</router-link>
        <button class="btn-logout" @click="handleLogout">Sign Out</button>
      </div>
    </header>

    <main class="platform-content">
      <section class="card">
        <h2>Welcome</h2>
        <p>
          Your identity has been verified. This is a placeholder for the main
          agent onboarding platform area. Feature modules can be added here later.
        </p>
      </section>
    </main>
  </div>
</template>

<script setup>
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
