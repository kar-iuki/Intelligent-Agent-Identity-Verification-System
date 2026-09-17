/**
 * Development utility: verify an agent's audit trail is complete.
 * Callable from scripts — no HTTP route required.
 */

import supabase from './supabaseClient.js'
import { ACTIONS, OUTCOMES } from './auditLogger.js'

const PIPELINE_CORE = [
  ACTIONS.AGENT_REGISTERED,
  ACTIONS.DOCUMENTS_UPLOADED,
  ACTIONS.VERIFICATION_INITIATED,
  ACTIONS.IMAGE_QUALITY_ASSESSED,
  ACTIONS.OCR_VERIFIED,
  ACTIONS.FACE_MATCH_COMPLETED,
  ACTIONS.LIVENESS_DETECTED,
  ACTIONS.KYC_DECISION_MADE,
]

/**
 * @param {string} agentID
 * @returns {Promise<{
 *   agentId: string,
 *   finalStatus: string|null,
 *   complete: boolean,
 *   present: string[],
 *   missing: string[],
 *   unexpectedOrder: boolean,
 *   entries: object[],
 * }>}
 */
export async function verifyAuditTrail(agentID) {
  if (!agentID) {
    throw new Error('agentID is required')
  }

  const { data: logs, error } = await supabase
    .from('audit_logs')
    .select('*')
    .eq('agent_id', agentID)
    .order('timestamp', { ascending: true })

  if (error) {
    throw new Error(error.message)
  }

  const entries = logs || []
  const actionsPresent = new Set(entries.map((row) => row.action))

  const { data: latestRequest } = await supabase
    .from('verification_requests')
    .select('status')
    .eq('agent_id', agentID)
    .order('created_at', { ascending: false })
    .limit(1)
    .maybeSingle()

  const finalStatus = latestRequest?.status || null
  const expected = [...PIPELINE_CORE]

  if (finalStatus === 'verified') {
    expected.push(ACTIONS.ACCESS_GRANTED)
  } else if (finalStatus === 'rejected') {
    expected.push(ACTIONS.ACCESS_DENIED)
  } else if (finalStatus === 'review') {
    expected.push(ACTIONS.MANUAL_REVIEW_FLAGGED)
    if (actionsPresent.has(ACTIONS.ADMIN_APPROVED)) {
      expected.push(ACTIONS.ADMIN_APPROVED, ACTIONS.ACCESS_GRANTED)
    } else if (actionsPresent.has(ACTIONS.ADMIN_REJECTED)) {
      expected.push(ACTIONS.ADMIN_REJECTED, ACTIONS.ACCESS_DENIED)
    }
  }

  // Quality-only rejection may skip OCR/face/liveness
  const qualityFailed = entries.some(
    (row) =>
      row.action === ACTIONS.IMAGE_QUALITY_ASSESSED
      && row.outcome === OUTCOMES.FAILED
  )

  let effectiveExpected = expected
  if (qualityFailed) {
    effectiveExpected = [
      ACTIONS.AGENT_REGISTERED,
      ACTIONS.DOCUMENTS_UPLOADED,
      ACTIONS.VERIFICATION_INITIATED,
      ACTIONS.IMAGE_QUALITY_ASSESSED,
      ACTIONS.KYC_DECISION_MADE,
      ACTIONS.ACCESS_DENIED,
    ]
  }

  const present = effectiveExpected.filter((action) => actionsPresent.has(action))
  const missing = effectiveExpected.filter((action) => !actionsPresent.has(action))

  const trailActions = entries
    .map((row) => row.action)
    .filter((action) => effectiveExpected.includes(action))

  let unexpectedOrder = false
  let cursor = 0
  for (const action of trailActions) {
    const index = effectiveExpected.indexOf(action, cursor)
    if (index === -1) {
      unexpectedOrder = true
      break
    }
    cursor = index
  }

  return {
    agentId: agentID,
    finalStatus,
    complete: missing.length === 0,
    present,
    missing,
    unexpectedOrder,
    expected: effectiveExpected,
    entries: entries.map((row) => ({
      action: row.action,
      outcome: row.outcome,
      timestamp: row.timestamp,
      performedBy: row.performed_by,
      details: row.details,
    })),
  }
}

export default verifyAuditTrail
