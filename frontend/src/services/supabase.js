import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    // We exchange the OAuth code ourselves in handleOAuthCallback to avoid
    // racing with detectSessionInUrl (double exchange → "PKCE verifier not found").
    detectSessionInUrl: false,
    flowType: 'pkce',
    persistSession: true,
    autoRefreshToken: true,
    storage: {
      getItem(key) { try { return window.localStorage.getItem(key) } catch { return null } },
      setItem(key, value) { try { window.localStorage.setItem(key, value) } catch { /* Optional persistence. */ } },
      removeItem(key) { try { window.localStorage.removeItem(key) } catch { /* Optional persistence. */ } },
    },
  },
})

export default supabase
