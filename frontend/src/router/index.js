import { createRouter, createWebHistory } from 'vue-router'
import { getAuthToken } from '../utils/authToken.js'
import LoginPage from '../views/LoginPage.vue'
import RegisterPage from '../views/RegisterPage.vue'
import PendingVerificationPage from '../views/PendingVerificationPage.vue'
import CompleteProfilePage from '../views/CompleteProfilePage.vue'
import AgentDashboard from '../views/AgentDashboard.vue'
import AdminDashboard from '../views/AdminDashboard.vue'

const routes = [
  {
    path: '/',
    redirect: '/login',
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: { guest: true },
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterPage,
    meta: { guest: true },
  },
  {
    path: '/pending',
    name: 'pending',
    component: PendingVerificationPage,
    meta: { guest: true },
  },
  {
    path: '/complete-profile',
    name: 'complete-profile',
    component: CompleteProfilePage,
    meta: { requiresAuth: true, allowIncomplete: true },
  },
  {
    path: '/agent/dashboard',
    name: 'agent-dashboard',
    component: AgentDashboard,
    meta: { requiresAuth: true, role: 'agent' },
  },
  {
    path: '/admin/dashboard',
    name: 'admin-dashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'admin' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const token = getAuthToken()
  const role = localStorage.getItem('auth_role')
  const isAuthenticated = !!token

  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      return next('/login')
    }

    if (to.meta.role && role !== to.meta.role) {
      if (!role && to.meta.allowIncomplete) {
        return next()
      }
      if (!role) {
        return next('/complete-profile')
      }
      return next('/login')
    }
  }

  if (to.meta.guest && isAuthenticated && role) {
    const dashboard = role === 'admin' ? '/admin/dashboard' : '/agent/dashboard'
    if (to.path === '/login') {
      return next(dashboard)
    }
  }

  if (to.path === '/login' && isAuthenticated && !role) {
    return next('/complete-profile')
  }

  next()
})

export default router
