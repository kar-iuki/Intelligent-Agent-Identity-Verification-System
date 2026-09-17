/**
 * Centralised audit logging utility (Module 10).
 * All controllers/middleware must write AuditLogs through logAction.
 */

import supabase from './supabaseClient.js'

export const ACTIONS = {
  AGENT_REGISTERED: 'AGENT_REGISTERED',
  DOCUMENTS_UPLOADED: 'DOCUMENTS_UPLOADED',
  VERIFICATION_INITIATED: 'VERIFICATION_INITIATED',
  IMAGE_QUALITY_ASSESSED: 'IMAGE_QUALITY_ASSESSED',
  OCR_VERIFIED: 'OCR_VERIFIED',
  FACE_MATCH_COMPLETED: 'FACE_MATCH_COMPLETED',
  LIVENESS_DETECTED: 'LIVENESS_DETECTED',
  KYC_DECISION_MADE: 'KYC_DECISION_MADE',
  ACCESS_GRANTED: 'ACCESS_GRANTED',
  ACCESS_DENIED: 'ACCESS_DENIED',
  MANUAL_REVIEW_FLAGGED: 'MANUAL_REVIEW_FLAGGED',
  ADMIN_APPROVED: 'ADMIN_APPROVED',
  ADMIN_REJECTED: 'ADMIN_REJECTED',
  FRAUD_GUARDRAIL_TRIGGERED: 'FRAUD_GUARDRAIL_TRIGGERED',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILED: 'LOGIN_FAILED',
  LOGOUT: 'LOGOUT',
}

export const OUTCOMES = {
  SUCCESS: 'SUCCESS',
  FAILED: 'FAILED',
  PASSED: 'PASSED',
  BORDERLINE: 'BORDERLINE',
  VERIFIED: 'VERIFIED',
  REVIEW: 'REVIEW',
  REJECTED: 'REJECTED',
  BLOCKED: 'BLOCKED',
}

/**
 * Insert an audit log row. Never throws — returns null on failure.
 *
 * @param {{
 *   agentID?: string|null,
 *   requestID?: string|null,
 *   action: string,
 *   outcome: string,
 *   details?: object|null,
 *   performedBy?: string|null,
 *   ipAddress?: string|null,
 *   deviceFingerprint?: string|null,
 * }} params
 */
export async function logAction(params = {}) {
  try {
    const {
      agentID = null,
      requestID = null,
      action,
      outcome,
      details = null,
      performedBy = null,
      ipAddress = null,
      deviceFingerprint = null,
    } = params

    if (!action || !outcome) {
      console.error('logAction: action and outcome are required')
      return null
    }

    const payload = {
      agent_id: agentID || null,
      request_id: requestID || null,
      action,
      outcome,
      timestamp: new Date().toISOString(),
    }

    if (details !== undefined && details !== null) {
      payload.details = details
    }

    if (performedBy !== undefined && performedBy !== null) {
      payload.performed_by = String(performedBy)
    }

    if (ipAddress) {
      payload.ip_address = String(ipAddress)
    }

    if (deviceFingerprint) {
      payload.device_fingerprint = String(deviceFingerprint)
    }

    const { data, error } = await supabase
      .from('audit_logs')
      .insert(payload)
      .select()
      .single()

    if (error) {
      console.error('Failed to write audit log:', error.message)
      return null
    }

    return data
  } catch (err) {
    console.error('Failed to write audit log:', err.message || err)
    return null
  }
}

/**
 * Map a continuous score to PASSED / BORDERLINE / FAILED.
 */
export function scoreToOutcome(value, passThreshold, borderThreshold) {
  const score = Number(value)
  if (Number.isNaN(score)) return OUTCOMES.FAILED
  if (score >= passThreshold) return OUTCOMES.PASSED
  if (score >= borderThreshold) return OUTCOMES.BORDERLINE
  return OUTCOMES.FAILED
}

export default logAction
