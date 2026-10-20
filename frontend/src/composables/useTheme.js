import { readonly, ref } from 'vue'

const STORAGE_KEY = 'verity-theme'
const theme = ref('light')

function applyTheme(next) {
  theme.value = next === 'dark' ? 'dark' : 'light'
  document.documentElement.dataset.theme = theme.value
  try { localStorage.setItem(STORAGE_KEY, theme.value) } catch { /* Optional persistence. */ }
}

export function initTheme() {
  let saved = null
  try { saved = localStorage.getItem(STORAGE_KEY) } catch { saved = null }
  applyTheme(saved === 'dark' ? 'dark' : 'light')
}

export function useTheme() {
  function toggleTheme() {
    applyTheme(theme.value === 'dark' ? 'light' : 'dark')
  }

  return { theme: readonly(theme), toggleTheme }
}
