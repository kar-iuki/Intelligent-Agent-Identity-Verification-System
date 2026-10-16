<template>
  <div class="app-shell" :class="{ 'is-collapsed': collapsed, 'menu-open': mobileOpen }">
    <a class="skip-link" href="#workspace-main">Skip to content</a>
    <button v-if="mobileOpen" class="nav-scrim" aria-label="Close navigation" @click="closeMenu" />
    <aside ref="sidebar" id="workspace-navigation" class="app-sidebar" aria-label="Workspace navigation" @keydown="trapFocus">
      <router-link :to="home" class="brand" aria-label="Verity home"><span class="brand-mark"><ShieldCheck :size="23" /></span><span class="nav-copy">Verity<span class="brand-caption">IDENTITY WORKSPACE</span></span></router-link>
      <div class="sidebar-label nav-copy">{{ admin ? 'ADMINISTRATION' : 'AGENT WORKSPACE' }}</div>
      <nav class="sidebar-links" aria-label="Main navigation">
        <router-link v-for="item in links" :key="item.to" :to="item.to" :class="{ selected: selected(item) }" :aria-current="selected(item) ? 'page' : undefined" :title="item.label" @click="mobileOpen = false">
          <component :is="item.icon" :size="19" aria-hidden="true" /><span class="nav-copy">{{ item.label }}</span><ChevronRight v-if="selected(item)" class="nav-indicator nav-copy" :size="14" />
        </router-link>
      </nav>
      <div class="sidebar-bottom">
        <div class="sidebar-note nav-copy"><ShieldCheck :size="20" /><strong>Identity starts with trust.</strong><p>Your verification and account tools, in one place.</p></div>
        <div class="sidebar-profile"><span class="profile-avatar">{{ initial }}</span><div class="nav-copy"><strong>{{ displayName }}</strong><span>{{ admin ? 'Administrator' : 'Agent account' }}</span></div></div>
        <button class="sidebar-signout" :disabled="signingOut" @click="signOut" title="Sign out"><LogOut :size="18" /><span class="nav-copy">{{ signingOut ? 'Signing out…' : 'Sign out' }}</span></button>
      </div>
    </aside>
    <div class="shell-body" :inert="mobile && mobileOpen">
      <header class="shell-topbar">
        <button ref="menuButton" class="icon-button" :aria-expanded="mobile ? mobileOpen : !collapsed" aria-controls="workspace-navigation" :aria-label="mobile ? 'Open navigation' : collapsed ? 'Expand sidebar' : 'Collapse sidebar'" @click="toggleNavigation"><PanelLeft :size="20" /></button>
        <span class="breadcrumb">{{ admin ? 'Administration' : 'Agent workspace' }}<ChevronRight :size="14" /><strong>{{ currentLabel }}</strong></span>
        <span class="topbar-account"><span class="account-dot" />{{ admin ? 'Admin' : 'Agent' }} portal</span>
      </header>
      <div id="workspace-main" tabindex="-1"><slot /></div>
      <footer class="workspace-footer">Verity <span>Intelligent Agent Identity Verification System</span></footer>
    </div>
  </div>
</template>
<script setup>
import { computed, ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ShieldCheck, LayoutDashboard, Fingerprint, History, BriefcaseBusiness, ChartNoAxesCombined, Users, Clock3, Flag, ChevronRight, PanelLeft, LogOut } from '@lucide/vue'
import { useAuthStore } from '../stores/authStore.js'
const route = useRoute(), router = useRouter()
const { state, logout } = useAuthStore()
const collapsed = ref(false), mobileOpen = ref(false), mobile = ref(false), signingOut = ref(false), menuButton = ref(null)
const sidebar = ref(null)
try { collapsed.value = localStorage.getItem('sidebar-collapsed') === 'true' } catch {}
const admin = computed(() => state.role === 'admin')
const home = computed(() => admin.value ? '/admin/dashboard' : '/agent/dashboard')
const links = computed(() => admin.value ? [
  { to: '/admin/dashboard?view=agents', label: 'Agent directory', icon: Users, view: 'agents' },
  { to: '/admin/dashboard?view=pending', label: 'Review queue', icon: Clock3, view: 'pending' },
  { to: '/admin/dashboard?view=recent', label: 'Recently verified', icon: ShieldCheck, view: 'recent' },
  { to: '/admin/dashboard?view=flagged', label: 'Flagged registrations', icon: Flag, view: 'flagged' },
  { to: '/admin/dashboard?view=audit', label: 'Audit log', icon: History, view: 'audit' },
  { to: '/admin/model', label: 'Model performance', icon: ChartNoAxesCombined },
] : [
  { to: '/agent/dashboard', label: 'Identity overview', icon: LayoutDashboard },
  { to: '/agent/platform', label: 'My workspace', icon: BriefcaseBusiness },
  { to: '/agent/audit', label: 'Activity history', icon: History },
  { to: '/agent/passkeys', label: 'Passkeys & security', icon: Fingerprint },
])
function selected(item) { return item.view ? route.path === '/admin/dashboard' && (route.query.view || 'agents') === item.view : route.path === item.to }
const currentLabel = computed(() => links.value.find(selected)?.label || 'Overview')
const displayName = computed(() => state.agent?.full_name || state.user?.email || (admin.value ? 'Administrator' : 'Agent'))
const initial = computed(() => displayName.value[0]?.toUpperCase())
function toggleNavigation() { if (mobile.value) mobileOpen.value = !mobileOpen.value; else { collapsed.value = !collapsed.value; try { localStorage.setItem('sidebar-collapsed', String(collapsed.value)) } catch {} } }
async function closeMenu() { mobileOpen.value = false; await nextTick(); menuButton.value?.focus() }
watch(mobileOpen, async (open) => { if (open) { await nextTick(); sidebar.value?.querySelector('a')?.focus() } })
function trapFocus(event) {
  if (!mobileOpen.value || event.key !== 'Tab') return
  const items = [...sidebar.value.querySelectorAll('a, button:not(:disabled)')]
  const first = items[0], last = items[items.length - 1]
  if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus() }
  else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus() }
}
function resize() { mobile.value = window.innerWidth <= 800; if (!mobile.value) mobileOpen.value = false }
function escapeMenu(event) { if (event.key === 'Escape' && mobileOpen.value) closeMenu() }
watch(() => route.fullPath, () => { mobileOpen.value = false })
onMounted(() => { resize(); window.addEventListener('resize', resize); window.addEventListener('keydown', escapeMenu) })
onBeforeUnmount(() => { window.removeEventListener('resize', resize); window.removeEventListener('keydown', escapeMenu) })
async function signOut() { signingOut.value = true; try { await logout(); await router.push('/login') } finally { signingOut.value = false } }
</script>
