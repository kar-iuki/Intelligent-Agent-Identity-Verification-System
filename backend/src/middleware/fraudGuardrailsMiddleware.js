import supabase from '../utils/supabaseClient.js'
import { logAction, ACTIONS, OUTCOMES } from '../utils/auditLogger.js'
import {
  fraudConfig,
  isBlockedEmailDomain,
  isFraudConfigValid,
} from '../config/fraudConfig.js'

isFraudConfigValid()

function hoursAgoIso(hours = fraudConfig.lookbackHours) {
  return new Date(Date.now() - hours * 60 * 60 * 1000).toISOString()
}

async function resolveAgentId(userId) {
  if (!userId) return null
  const { data } = await supabase
    .from('agents')
    .select('agent_id')
    .eq('user_id', userId)
    .maybeSingle()
  return data?.agent_id || null
}

async function getLatestVerificationStatus(agentId) {
  const { data } = await supabase
    .from('verification_requests')
    .select('status')
    .eq('agent_id', agentId)
    .order('created_at', { ascending: false })
    .limit(1)
    .maybeSingle()

  return data?.status || 'pending'
}

function nationalIdConflictMessage(status) {
  if (status === 'verified') {
    return 'This national ID is already registered to a verified agent'
  }
  if (status === 'rejected') {
    return 'This national ID has been previously rejected. Please contact support.'
  }
  return 'A registration with this national ID is already in progress'
}

async function countFraudAndFailedInit({ ipAddress = null, deviceFingerprint = null }) {
  const since = hoursAgoIso()
  let fraudQuery = supabase
    .from('audit_logs')
    .select('log_id, timestamp', { count: 'exact' })
    .eq('action', ACTIONS.FRAUD_GUARDRAIL_TRIGGERED)
    .gte('timestamp', since)
    .order('timestamp', { ascending: true })

  let failedInitQuery = supabase
    .from('audit_logs')
    .select('log_id, timestamp', { count: 'exact' })
    .eq('action', ACTIONS.VERIFICATION_INITIATED)
    .eq('outcome', OUTCOMES.FAILED)
    .gte('timestamp', since)
    .order('timestamp', { ascending: true })

  if (ipAddress) {
    fraudQuery = fraudQuery.eq('ip_address', ipAddress)
    failedInitQuery = failedInitQuery.eq('ip_address', ipAddress)
  } else if (deviceFingerprint) {
    fraudQuery = fraudQuery.eq('device_fingerprint', deviceFingerprint)
    failedInitQuery = failedInitQuery.eq('device_fingerprint', deviceFingerprint)
  } else {
    return { total: 0, oldestTimestamp: null }
  }

  const [fraudRes, failedRes] = await Promise.all([fraudQuery, failedInitQuery])

  if (fraudRes.error) console.error('fraud count error:', fraudRes.error.message)
  if (failedRes.error) console.error('failed init count error:', failedRes.error.message)

  const fraudRows = fraudRes.data || []
  const failedRows = failedRes.data || []
  const total = (fraudRes.count ?? fraudRows.length) + (failedRes.count ?? failedRows.length)

  const timestamps = [...fraudRows, ...failedRows]
    .map((row) => row.timestamp)
    .filter(Boolean)
    .sort()

  return {
    total,
    oldestTimestamp: timestamps[0] || null,
  }
}

function retryAfterSeconds(oldestTimestamp) {
  if (!oldestTimestamp) {
    return fraudConfig.lookbackHours * 60 * 60
  }
  const unlockAt =
    new Date(oldestTimestamp).getTime() + fraudConfig.lookbackHours * 60 * 60 * 1000
  return Math.max(1, Math.ceil((unlockAt - Date.now()) / 1000))
}

async function triggerGuardrail(res, {
  agentId,
  guardrailType,
  ipAddress,
  deviceFingerprint,
  attemptCount,
  status,
  message,
  oldestTimestamp = null,
  extraDetails = {},
}) {
  await logAction({
    agentID: agentId,
    action: ACTIONS.FRAUD_GUARDRAIL_TRIGGERED,
    outcome: OUTCOMES.BLOCKED,
    performedBy: 'system',
    ipAddress: ipAddress || null,
    deviceFingerprint: deviceFingerprint || null,
    details: {
      guardrailType,
      ipAddress: ipAddress || null,
      deviceFingerprint: deviceFingerprint || null,
      attemptCount,
      ...extraDetails,
    },
  })

  if (status === 429) {
    res.setHeader('Retry-After', String(retryAfterSeconds(oldestTimestamp)))
  }

  return res.status(status).json({ error: message })
}

/**
 * Fraud guardrails for POST /api/agent/registration
 */
export default async function fraudGuardrailsMiddleware(req, res, next) {
  try {
    const { nationalID, deviceFingerprint: bodyFingerprint, email: bodyEmail } = req.body || {}
    const ipAddress = req.clientIP || null
    const deviceFingerprint = bodyFingerprint ? String(bodyFingerprint) : null
    const agentId = await resolveAgentId(req.user?.id)
    const email = bodyEmail || req.user?.email || null

    // Email domain check
    if (email && isBlockedEmailDomain(email)) {
      return triggerGuardrail(res, {
        agentId,
        guardrailType: 'blocked_email_domain',
        ipAddress,
        deviceFingerprint,
        attemptCount: 1,
        status: 400,
        message: 'Please use a valid permanent email address to register',
        extraDetails: {
          blockedDomain: email.trim().toLowerCase().split('@')[1] || null,
        },
      })
    }

    // Duplicate national ID check
    if (nationalID) {
      const { data: existing, error } = await supabase
        .from('agents')
        .select('agent_id')
        .eq('national_id', String(nationalID).trim())
        .maybeSingle()

      if (error) {
        return res.status(500).json({ error: error.message })
      }

      if (existing && existing.agent_id !== agentId) {
        const status = await getLatestVerificationStatus(existing.agent_id)
        return triggerGuardrail(res, {
          agentId,
          guardrailType: 'duplicate_national_id',
          ipAddress,
          deviceFingerprint,
          attemptCount: 1,
          status: 409,
          message: nationalIdConflictMessage(status),
          extraDetails: {
            conflictingAgentId: existing.agent_id,
            conflictingStatus: status,
          },
        })
      }
    }

    // IP rate limiting
    if (ipAddress) {
      const { total, oldestTimestamp } = await countFraudAndFailedInit({ ipAddress })
      if (total >= fraudConfig.maxFailedAttemptsPerIp) {
        return triggerGuardrail(res, {
          agentId,
          guardrailType: 'ip_rate_limit',
          ipAddress,
          deviceFingerprint,
          attemptCount: total,
          status: 429,
          message: `Too many failed attempts from this location. Please try again in ${fraudConfig.lookbackHours} hours.`,
          oldestTimestamp,
        })
      }
    }

    // Device fingerprint check
    if (deviceFingerprint) {
      const { total, oldestTimestamp } = await countFraudAndFailedInit({ deviceFingerprint })
      if (total >= fraudConfig.maxFailedAttemptsPerDevice) {
        return triggerGuardrail(res, {
          agentId,
          guardrailType: 'device_fingerprint_rate_limit',
          ipAddress,
          deviceFingerprint,
          attemptCount: total,
          status: 429,
          message: `Too many failed attempts from this device. Please try again in ${fraudConfig.lookbackHours} hours.`,
          oldestTimestamp,
        })
      }
    }

    req.deviceFingerprint = deviceFingerprint
    return next()
  } catch (err) {
    console.error('fraudGuardrailsMiddleware error:', err)
    return res.status(500).json({ error: 'Fraud check failed' })
  }
}

export { nationalIdConflictMessage, getLatestVerificationStatus }
