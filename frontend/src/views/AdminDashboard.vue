<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <h1>Admin Dashboard</h1>
      <button class="btn-logout" @click="handleLogout">Sign Out</button>
    </header>

    <div class="dashboard-content">
      <div class="welcome-card">
        <h2>Welcome, {{ displayName }}</h2>
        <p class="role-badge">Role: {{ role }}</p>
        <p class="info">You are signed in as an administrator. Management features will be available in a later module.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'

const router = useRouter()
const { state, logout, fetchCurrentUser } = useAuthStore()

onMounted(async () => {
  await fetchCurrentUser()
})

const displayName = computed(() => {
  return state.user?.email || 'Administrator'
})

const role = computed(() => state.role || 'admin')

async function handleLogout() {
  await logout()
  router.push('/login')
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #f0f4f8;
}

.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 2rem;
  background: #fff;
  border-bottom: 1px solid #d9e2ec;
}

h1 {
  font-size: 1.25rem;
  color: #16213e;
}

.btn-logout {
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid #d9e2ec;
  border-radius: 8px;
  color: #52606d;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-logout:hover {
  background: #f0f4f8;
}

.dashboard-content {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.welcome-card {
  background: #fff;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

h2 {
  font-size: 1.375rem;
  color: #16213e;
  margin-bottom: 0.5rem;
}

.role-badge {
  display: inline-block;
  background: #fce8e8;
  color: #9b2c2c;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8125rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.info {
  color: #52606d;
  line-height: 1.6;
}
</style>
