import supabase from '../utils/supabaseClient.js'
import { logAction, ACTIONS, OUTCOMES } from '../utils/auditLogger.js'
import { fraudConfig } from '../config/fraudConfig.js'

function hoursAgoIso(hours) {
  return new Date(Date.now() - hours * 60 * 60 * 1000).toISOString()
}

async function getLastStrikeResetAt(agentID) {
  const { data, error } = await supabase
    .from('audit_logs')
    .select('timestamp, details')
    .eq('agent_id', agentID)
    .eq('action', ACTIONS.ADMIN_APPROVED)
    .order('timestamp', { ascending: false })
    .limit(50)

  if (error) {
    console.error('getLastStrikeResetAt error:', error.message)
    return null
  }

  const resetEntry = (data || []).find((row) => row.details?.strikesReset === true)
  return resetEntry?.timestamp || null
}

/**
 * Total failed verification strikes for an agent within the lookback window
 * (ignoring strikes recorded before the last admin reset).
 */
export async function getStrikeCount(agentID) {
  if (!agentID) return 0

  const lookbackSince = hoursAgoIso(fraudConfig.lookbackHours)
  const resetAt = await getLastStrikeResetAt(agentID)
  const since =
    resetAt && new Date(resetAt) > new Date(lookbackSince) ? resetAt : lookbackSince

  const { data, error } = await supabase
    .from('audit_logs')
    .select('log_id, details')
    .eq('agent_id', agentID)
    .eq('action', ACTIONS.FRAUD_GUARDRAIL_TRIGGERED)
    .gte('timestamp', since)

  if (error) {
    console.error('getStrikeCount error:', error.message)
    return 0
  }

  return (data || []).filter(
    (row) => row.details?.guardrailType === 'verification_strike'
  ).length
}

/**
 * Record a verification failure strike. Auto-rejects when the threshold is hit.
 */
export async function recordStrike(agentID, ipAddress, deviceFingerprint, reason) {
  if (!agentID) {
    console.warn('recordStrike called without agentID')
    return { strikeCount: 0, autoRejected: false }
  }

  await logAction({
    agentID,
    action: ACTIONS.FRAUD_GUARDRAIL_TRIGGERED,
    outcome: OUTCOMES.BLOCKED,
    performedBy: 'system',
    ipAddress: ipAddress || null,
    deviceFingerprint: deviceFingerprint || null,
    details: {
      guardrailType: 'verification_strike',
      ipAddress: ipAddress || null,
      deviceFingerprint: deviceFingerprint || null,
      reason: reason || 'verification_failed',
      strikes: true,
    },
  })

  const strikeCount = await getStrikeCount(agentID)
  let autoRejected = false

  if (strikeCount >= fraudConfig.maxStrikesBeforeReject) {
    autoRejected = true

    const { data: latestRequest } = await supabase
      .from('verification_requests')
      .select('request_id, status')
      .eq('agent_id', agentID)
      .order('created_at', { ascending: false })
      .limit(1)
      .maybeSingle()

    if (latestRequest && latestRequest.status !== 'rejected') {
      await supabase
        .from('verification_requests')
        .update({ status: 'rejected' })
        .eq('request_id', latestRequest.request_id)
    }

    await logAction({
      agentID,
      requestID: latestRequest?.request_id || null,
      action: ACTIONS.ACCESS_DENIED,
      outcome: OUTCOMES.REJECTED,
      performedBy: 'system',
      ipAddress: ipAddress || null,
      deviceFingerprint: deviceFingerprint || null,
      details: {
        reason: 'Maximum verification attempts exceeded',
        strikeCount,
        threshold: fraudConfig.maxStrikesBeforeReject,
      },
    })
  }

  return { strikeCount, autoRejected }
}

/**
 * Clear strike counting for an agent (marks a reset in the immutable audit log).
 */
export async function resetStrikes(agentID, performedBy = 'system') {
  if (!agentID) {
    throw new Error('agentID is required')
  }

  const previousCount = await getStrikeCount(agentID)

  const log = await logAction({
    agentID,
    action: ACTIONS.ADMIN_APPROVED,
    outcome: OUTCOMES.SUCCESS,
    performedBy,
    details: {
      strikesReset: true,
      previousStrikeCount: previousCount,
      note: 'Administrator reset verification strike count',
    },
  })

  return {
    previousCount,
    log,
  }
}

export default {
  recordStrike,
  getStrikeCount,
  resetStrikes,
}
