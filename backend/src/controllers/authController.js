import supabase from '../utils/supabaseClient.js'
import supabaseAnon from '../utils/supabaseAnon.js'
import { logAction, ACTIONS, OUTCOMES } from '../utils/auditLogger.js'
import { isBlockedEmailDomain, extractEmailDomain } from '../config/fraudConfig.js'
import {
  nationalIdConflictMessage,
  getLatestVerificationStatus,
} from '../middleware/fraudGuardrailsMiddleware.js'
import { validateDateOfBirth } from '../utils/validateDateOfBirth.js'

async function resolveAgentIdForUser(userId) {
  if (!userId) return null
  const { data } = await supabase
    .from('agents')
    .select('agent_id')
    .eq('user_id', userId)
    .maybeSingle()
  return data?.agent_id || null
}

function extractSuggestedFullName(authUser) {
  const meta = authUser?.user_metadata || {}
  if (meta.full_name?.trim()) return meta.full_name.trim()
  if (meta.name?.trim()) return meta.name.trim()

  const given = meta.given_name?.trim() || ''
  const family = meta.family_name?.trim() || ''
  const combined = `${given} ${family}`.trim()
  return combined || null
}

function frontendUrl() {
  const raw = process.env.FRONTEND_URL || 'http://localhost:5173'
  // FRONTEND_URL may be comma-separated for CORS; email redirects use the first
  return raw.split(',')[0].trim() || 'http://localhost:5173'
}

export async function registerAgent(req, res) {
  const {
    fullName,
    email,
    password,
    confirmPassword,
    deviceFingerprint,
  } = req.body

  if (!fullName || !email || !password) {
    return res.status(400).json({ error: 'Full name, email, and password are required' })
  }

  if (!confirmPassword) {
    return res.status(400).json({ error: 'Please confirm your password' })
  }

  if (password !== confirmPassword) {
    return res.status(400).json({ error: 'Passwords do not match' })
  }

  if (String(password).length < 8) {
    return res.status(400).json({ error: 'Password must be at least 8 characters' })
  }

  if (isBlockedEmailDomain(email)) {
    await logAction({
      agentID: null,
      action: ACTIONS.FRAUD_GUARDRAIL_TRIGGERED,
      outcome: OUTCOMES.BLOCKED,
      performedBy: 'system',
      ipAddress: req.clientIP,
      deviceFingerprint: deviceFingerprint || null,
      details: {
        guardrailType: 'blocked_email_domain',
        ipAddress: req.clientIP || null,
        deviceFingerprint: deviceFingerprint || null,
        attemptCount: 1,
        blockedDomain: extractEmailDomain(email),
      },
    })
    return res.status(400).json({
      error: 'Please use a valid permanent email address to register',
    })
  }

  const normalizedEmail = String(email).trim().toLowerCase()

  const { data: authData, error: authError } = await supabaseAnon.auth.signUp({
    email: normalizedEmail,
    password,
    options: {
      emailRedirectTo: `${frontendUrl()}/login`,
      data: {
        full_name: String(fullName).trim(),
      },
    },
  })

  if (authError) {
    return res.status(400).json({ error: authError.message })
  }

  if (authData.user && Array.isArray(authData.user.identities) && authData.user.identities.length === 0) {
    return res.status(400).json({
      error: 'An account with this email already exists. Please sign in or verify your email.',
    })
  }

  // Confirm-email disabled: session exists immediately → finish profile next
  if (authData.session && authData.user) {
    return res.status(201).json({
      requiresEmailVerification: false,
      needsProfile: true,
      token: authData.session.access_token,
      refreshToken: authData.session.refresh_token,
      email: normalizedEmail,
      suggestedFullName: extractSuggestedFullName(authData.user),
      message: 'Account created. Complete your profile to continue.',
    })
  }

  return res.status(201).json({
    requiresEmailVerification: true,
    email: normalizedEmail,
    message: 'Check your email and click the confirmation link to continue.',
  })
}

export async function resendVerificationEmail(req, res) {
  const { email } = req.body

  if (!email) {
    return res.status(400).json({ error: 'Email is required' })
  }

  const normalizedEmail = String(email).trim().toLowerCase()

  const { error } = await supabaseAnon.auth.resend({
    type: 'signup',
    email: normalizedEmail,
    options: {
      emailRedirectTo: `${frontendUrl()}/login`,
    },
  })

  if (error) {
    return res.status(400).json({ error: error.message })
  }

  return res.json({
    message: 'A new confirmation email has been sent.',
    email: normalizedEmail,
  })
}

export async function login(req, res) {
  const { email, password } = req.body

  if (!email || !password) {
    return res.status(400).json({ error: 'Email and password are required' })
  }

  const { data, error } = await supabaseAnon.auth.signInWithPassword({ email, password })

  if (error) {
    await logAction({
      agentID: null,
      action: ACTIONS.LOGIN_FAILED,
      outcome: OUTCOMES.FAILED,
      performedBy: 'system',
      ipAddress: req.clientIP,
      details: { email, reason: error.message },
    })
    return res.status(401).json({ error: error.message })
  }

  const { data: userRecord, error: dbError } = await supabase
    .from('users')
    .select('*')
    .eq('user_id', data.user.id)
    .maybeSingle()

  // Email confirmed but agent profile not finished yet
  if (dbError || !userRecord) {
    return res.json({
      needsProfile: true,
      token: data.session.access_token,
      refreshToken: data.session.refresh_token,
      email: data.user.email,
      suggestedFullName: extractSuggestedFullName(data.user),
      user: null,
      role: null,
      agent: null,
    })
  }

  const agent =
    userRecord.role === 'agent'
      ? (await supabase.from('agents').select('*').eq('user_id', data.user.id).single()).data
      : null

  await logAction({
    agentID: agent?.agent_id || null,
    action: ACTIONS.LOGIN_SUCCESS,
    outcome: OUTCOMES.SUCCESS,
    performedBy: userRecord.user_id,
    ipAddress: req.clientIP,
    details: { email, role: userRecord.role },
  })

  return res.json({
    token: data.session.access_token,
    refreshToken: data.session.refresh_token,
    user: userRecord,
    role: userRecord.role,
    agent,
  })
}

export async function logout(req, res) {
  const authHeader = req.headers.authorization
  const token = authHeader?.split(' ')[1]

  if (!token) {
    return res.status(401).json({ error: 'Missing authorization token' })
  }

  const { data: { user }, error } = await supabase.auth.getUser(token)

  if (error || !user) {
    return res.status(401).json({ error: 'Invalid or expired token' })
  }

  const agentId = await resolveAgentIdForUser(user.id)

  const { error: signOutError } = await supabase.auth.admin.signOut(user.id)

  if (signOutError) {
    return res.status(500).json({ error: signOutError.message })
  }

  await logAction({
    agentID: agentId,
    action: ACTIONS.LOGOUT,
    outcome: OUTCOMES.SUCCESS,
    performedBy: user.id,
    ipAddress: req.clientIP,
  })

  return res.json({ message: 'Logged out successfully' })
}

export async function getMe(req, res) {
  if (!req.user.profileComplete) {
    return res.json({
      needsProfile: true,
      email: req.user.email,
      suggestedFullName: req.user.suggestedFullName || null,
      user: null,
      agent: null,
      role: null,
    })
  }

  const userId = req.user.id

  const { data: userRecord, error: userError } = await supabase
    .from('users')
    .select('*')
    .eq('user_id', userId)
    .single()

  if (userError || !userRecord) {
    return res.status(404).json({ error: 'User not found' })
  }

  let agent = null
  if (userRecord.role === 'agent') {
    const { data: agentRecord } = await supabase
      .from('agents')
      .select('*')
      .eq('user_id', userId)
      .single()
    agent = agentRecord
  }

  return res.json({
    needsProfile: false,
    user: userRecord,
    agent,
    role: userRecord.role,
  })
}

export async function completeOAuthProfile(req, res) {
  const { fullName, phoneNumber, nationalID, dateOfBirth } = req.body

  const resolvedName = (fullName || req.user.suggestedFullName || '').trim()

  if (!resolvedName || !phoneNumber || !nationalID || !dateOfBirth) {
    return res.status(400).json({
      error: 'Full name, phone number, national ID, and date of birth are required',
    })
  }

  const dobError = validateDateOfBirth(dateOfBirth)
  if (dobError) {
    return res.status(400).json({ error: dobError })
  }

  const userId = req.user.id
  const email = req.user.email

  if (req.user.profileComplete) {
    return res.status(400).json({ error: 'Profile is already complete' })
  }

  const { data: existingNationalId } = await supabase
    .from('agents')
    .select('agent_id')
    .eq('national_id', String(nationalID).trim())
    .maybeSingle()

  if (existingNationalId) {
    const status = await getLatestVerificationStatus(existingNationalId.agent_id)
    return res.status(409).json({ error: nationalIdConflictMessage(status) })
  }

  const { data: user, error: userError } = await supabase
    .from('users')
    .insert({ user_id: userId, email, role: 'agent' })
    .select()
    .single()

  if (userError) {
    return res.status(400).json({ error: userError.message })
  }

  const { data: agent, error: agentError } = await supabase
    .from('agents')
    .insert({
      user_id: userId,
      full_name: resolvedName,
      phone_number: String(phoneNumber).trim(),
      national_id: String(nationalID).trim(),
      date_of_birth: String(dateOfBirth).trim(),
    })
    .select()
    .single()

  if (agentError) {
    await supabase.from('users').delete().eq('user_id', userId)
    return res.status(400).json({ error: agentError.message })
  }

  // Keep auth metadata in sync
  await supabase.auth.admin.updateUserById(userId, {
    user_metadata: {
      full_name: resolvedName,
      phone_number: String(phoneNumber).trim(),
      national_id: String(nationalID).trim(),
      date_of_birth: String(dateOfBirth).trim(),
    },
  })

  await logAction({
    agentID: agent.agent_id,
    action: ACTIONS.AGENT_REGISTERED,
    outcome: OUTCOMES.SUCCESS,
    performedBy: userId,
    ipAddress: req.clientIP,
    details: { email, source: 'complete_profile' },
  })

  return res.status(201).json({
    user,
    agent,
    role: user.role,
  })
}
