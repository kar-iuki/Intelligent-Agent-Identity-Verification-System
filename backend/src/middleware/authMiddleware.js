import supabase from '../utils/supabaseClient.js'

export default async function authMiddleware(req, res, next) {
  const authHeader = req.headers.authorization

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing or invalid authorization token' })
  }

  const token = authHeader.split(' ')[1]

  const { data: { user }, error } = await supabase.auth.getUser(token)

  if (error || !user) {
    return res.status(401).json({ error: 'Invalid or expired token' })
  }

  const { data: userRecord } = await supabase
    .from('users')
    .select('*')
    .eq('user_id', user.id)
    .single()

  const meta = user.user_metadata || {}
  const suggestedFullName =
    meta.full_name?.trim()
    || meta.name?.trim()
    || `${meta.given_name || ''} ${meta.family_name || ''}`.trim()
    || null

  req.user = {
    id: user.id,
    email: user.email,
    role: userRecord?.role || null,
    profileComplete: !!userRecord,
    suggestedFullName,
    ...(userRecord || {}),
  }

  next()
}

export function requireCompleteProfile(req, res, next) {
  if (!req.user?.profileComplete) {
    return res.status(403).json({
      error: 'Profile incomplete',
      needsProfile: true,
    })
  }
  next()
}
