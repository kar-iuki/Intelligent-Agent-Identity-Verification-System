export const ACTION_LABELS = {
  AGENT_REGISTERED: 'Account registered',
  DOCUMENTS_UPLOADED: 'Documents uploaded',
  VERIFICATION_INITIATED: 'Verification started',
  IMAGE_QUALITY_ASSESSED: 'Document quality checked',
  OCR_VERIFIED: 'Document text verified',
  FACE_MATCH_COMPLETED: 'Face match completed',
  LIVENESS_DETECTED: 'Liveness check completed',
  KYC_DECISION_MADE: 'Verification decision made',
  ACCESS_GRANTED: 'Platform access granted',
  ACCESS_DENIED: 'Platform access denied',
  MANUAL_REVIEW_FLAGGED: 'Flagged for manual review',
  ADMIN_APPROVED: 'Approved by administrator',
  ADMIN_REJECTED: 'Rejected by administrator',
  FRAUD_GUARDRAIL_TRIGGERED: 'Fraud guardrail triggered',
  LOGIN_SUCCESS: 'Signed in successfully',
  LOGIN_FAILED: 'Sign-in failed',
  LOGOUT: 'Signed out',
}

export function labelForAction(action) {
  return ACTION_LABELS[action] || action
}
