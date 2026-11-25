// Legacy reviews without a recoverable system event contain admin-set 0/1
// values. Never return those as classifier probabilities.
export function automatedDecision(row) {
  if (row?.decision_basis !== 'legacy_admin_override') return row
  return {
    ...row, final_decision: null, decided_at: null,
    verified_probability: null, review_probability: null, rejected_probability: null,
  }
}
