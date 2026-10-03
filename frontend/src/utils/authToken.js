const TOKEN_KEY = 'auth_token'
let memoryToken = null

export function setAuthToken(token) {
  memoryToken = token || null
  try {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token)
  } else {
    localStorage.removeItem(TOKEN_KEY)
  }
  } catch { /* Keep the session usable when browser storage is blocked. */ }
}

export function getAuthToken() {
  try { return localStorage.getItem(TOKEN_KEY) || memoryToken } catch { return memoryToken }
}

export function clearAuthToken() {
  setAuthToken(null)
}
