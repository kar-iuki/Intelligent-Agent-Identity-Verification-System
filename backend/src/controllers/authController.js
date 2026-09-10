import supabase from '../utils/supabaseClient.js'
import supabaseAnon from '../utils/supabaseAnon.js'

export async function registerAgent(req, res) {
  const { fullName, email, password, phoneNumber, nationalID } = req.body

  if (!fullName || !email || !password || !phoneNumber || !nationalID) {
    return res.status(400).json({ error: 'All fields are required' })
  }

  const { data: authData, error: authError } = await supabase.auth.admin.createUser({
    email,
    password,
    email_confirm: true,
  })

  if (authError) {
    return res.status(400).json({ error: authError.message })
  }

  const userId = authData.user.id

  const { data: user, error: userError } = await supabase
    .from('users')
    .insert({ user_id: userId, email, role: 'agent' })
    .select()
    .single()

  if (userError) {
    await supabase.auth.admin.deleteUser(userId)
    return res.status(400).json({ error: userError.message })
  }

  const { data: agent, error: agentError } = await supabase
    .from('agents')
    .insert({
      user_id: userId,
      full_name: fullName,
      phone_number: phoneNumber,
      national_id: nationalID,
    })
    .select()
    .single()

  if (agentError) {
    await supabase.from('users').delete().eq('user_id', userId)
    await supabase.auth.admin.deleteUser(userId)
    return res.status(400).json({ error: agentError.message })
  }

  return res.status(201).json({ user, agent })
}

export async function login(req, res) {
  const { email, password } = req.body

  if (!email || !password) {
    return res.status(400).json({ error: 'Email and password are required' })
  }

  const { data, error } = await supabaseAnon.auth.signInWithPassword({ email, password })

  if (error) {
    return res.status(401).json({ error: error.message })
  }

  const { data: userRecord, error: dbError } = await supabase
    .from('users')
    .select('*')
    .eq('user_id', data.user.id)
    .single()

  if (dbError || !userRecord) {
    return res.status(401).json({ error: 'User account not found' })
  }

  return res.json({
    token: data.session.access_token,
    refreshToken: data.session.refresh_token,
    user: userRecord,
    role: userRecord.role,
    agent: userRecord.role === 'agent'
      ? (await supabase.from('agents').select('*').eq('user_id', data.user.id).single()).data
      : null,
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

  const { error: signOutError } = await supabase.auth.admin.signOut(user.id)

  if (signOutError) {
    return res.status(500).json({ error: signOutError.message })
  }

  return res.json({ message: 'Logged out successfully' })
}

export async function getMe(req, res) {
  if (!req.user.profileComplete) {
    return res.json({
      needsProfile: true,
      email: req.user.email,
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
  const { fullName, phoneNumber, nationalID } = req.body

  if (!fullName || !phoneNumber || !nationalID) {
    return res.status(400).json({
      error: 'Full name, phone number, and national ID are required',
    })
  }

  const userId = req.user.id
  const email = req.user.email

  if (req.user.profileComplete) {
    return res.status(400).json({ error: 'Profile is already complete' })
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
      full_name: fullName,
      phone_number: phoneNumber,
      national_id: nationalID,
    })
    .select()
    .single()

  if (agentError) {
    await supabase.from('users').delete().eq('user_id', userId)
    return res.status(400).json({ error: agentError.message })
  }

  return res.status(201).json({
    user,
    agent,
    role: user.role,
  })
}
