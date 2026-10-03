import { ref, onMounted, onBeforeUnmount } from 'vue'

export async function detectPasskeySupport(win = typeof window === 'undefined' ? undefined : window) {
  try {
    const credential = win?.PublicKeyCredential
    if (!credential || win.isSecureContext === false) return { supported: false, conditionalUI: false }
    const supported = await credential.isUserVerifyingPlatformAuthenticatorAvailable()
    const conditionalUI = !!(await credential.isConditionalMediationAvailable?.())
    return { supported: !!supported, conditionalUI }
  } catch { return { supported: false, conditionalUI: false } }
}
export function usePasskeySupport() {
  const supported = ref(false)
  const conditionalUI = ref(false)
  let active = true
  onMounted(async () => {
    const result = await detectPasskeySupport()
    if (active) { supported.value = result.supported; conditionalUI.value = result.conditionalUI }
  })
  onBeforeUnmount(() => { active = false })
  return { supported, conditionalUI }
}
