import { createRouter, createWebHistory } from 'vue-router'
import { getAuthToken } from '../utils/authToken.js'
import { useAuthStore } from '../stores/authStore.js'
import LoginPage from '../views/LoginPage.vue'
import ForgotPasswordPage from '../views/ForgotPasswordPage.vue'
import ResetPasswordPage from '../views/ResetPasswordPage.vue'
import RegisterPage from '../views/RegisterPage.vue'
import CheckEmailPage from '../views/CheckEmailPage.vue'
import PendingVerificationPage from '../views/PendingVerificationPage.vue'
import CompleteProfilePage from '../views/CompleteProfilePage.vue'
import AgentDashboard from '../views/AgentDashboard.vue'
import AgentAuditLog from '../views/AgentAuditLog.vue'
import AgentPlatformPage from '../views/AgentPlatformPage.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import AdminModelEvaluation from '../views/AdminModelEvaluation.vue'

const routes = [
  {
    path: '/agent/passkeys',
    name: 'agent-passkeys',
    component: () => import('../views/ManagePasskeysPage.vue'),
    meta: { requiresAuth: true, role: 'agent' },
  },
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomeView.vue'),
    meta: { landing: true },
    beforeEnter: (to) => {
      const hashParams = new URLSearchParams(to.hash.replace(/^#/, ''))
      // Email and OAuth links can still return to the site root.
      const callbackKeys = ['access_token', 'code', 'token_hash', 'error', 'error_code', 'error_description', 'type']
      if (!callbackKeys.some(key => hashParams.has(key) || to.query[key] !== undefined)) return true
      const type = (hashParams.get('type') || to.query.type || '').toString().toLowerCase()
      const path = (hashParams.get('access_token') || to.query.access_token) && type === 'recovery'
        ? '/reset-password'
        : '/login'
      return { path, hash: to.hash, query: to.query }
    },
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: { guest: true },
  },
  {
    path: '/forgot-password',
    name: 'forgot-password',
    component: ForgotPasswordPage,
    meta: { guest: true },
  },
  {
    path: '/reset-password',
    name: 'reset-password',
    component: ResetPasswordPage,
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterPage,
    meta: { guest: true },
  },
  {
    path: '/check-email',
    name: 'check-email',
    component: CheckEmailPage,
    meta: { guest: true },
  },
  {
    path: '/verify-email',
    redirect: '/check-email',
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
    path: '/agent/audit',
    name: 'agent-audit',
    component: AgentAuditLog,
    meta: { requiresAuth: true, role: 'agent' },
  },
  {
    path: '/agent/platform',
    name: 'agent-platform',
    component: AgentPlatformPage,
    meta: { requiresAuth: true, role: 'agent' },
  },
  {
    path: '/admin/dashboard',
    name: 'admin-dashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/admin/model',
    name: 'admin-model',
    component: AdminModelEvaluation,
    meta: { requiresAuth: true, role: 'admin' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.meta.landing && ['#how-it-works', '#why-verity', '#questions', '#main-content'].includes(to.hash)) {
      return { el: to.hash, top: 100, behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' }
    }
    if (to.path !== from.path) return { top: 0 }
  },
})

router.beforeEach((to, _from, next) => {
  const token = getAuthToken()
  const role = useAuthStore().state.role
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
