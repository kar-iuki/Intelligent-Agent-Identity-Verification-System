import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.SUPABASE_URL
const supabaseAnonKey = process.env.SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error(
    'Missing Supabase environment variables. Ensure SUPABASE_URL and SUPABASE_ANON_KEY are set in .env'
  )
}

const supabaseAnon = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false,
    // Email confirmation and password-reset links must work in any browser.
    // PKCE would store the code verifier on this server, not in the user's browser.
    flowType: 'implicit',
  },
})

export default supabaseAnon
