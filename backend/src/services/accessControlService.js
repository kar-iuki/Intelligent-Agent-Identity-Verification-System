/**
 * Placeholder threshold access-control rules (Module 8).
 * Replaced by the trained SVM classifier in Module 12.
 */

export function applyPlaceholderDecision(scores) {
  const faceMatchScore = Number(scores.faceMatchScore ?? scores.face_match_score ?? 0)
  const livenessScore = Number(scores.livenessScore ?? scores.liveness_score ?? 0)
  const ocrConfidenceScore = Number(
    scores.ocrConfidenceScore ?? scores.ocr_confidence_score ?? 0
  )
  const blurScore = Number(scores.blurScore ?? scores.blur_score ?? 0)
  const brightnessScore = Number(scores.brightnessScore ?? scores.brightness_score ?? 0)
  const contrastScore = Number(scores.contrastScore ?? scores.contrast_score ?? 0)

  const reasons = []

  // Rejected conditions (checked first)
  if (faceMatchScore < 50.0) {
    reasons.push(`Face match score ${faceMatchScore} is below 50.0`)
  }
  if (livenessScore < 0.5) {
    reasons.push(`Liveness score ${livenessScore} is below 0.50`)
  }
  if (ocrConfidenceScore < 0.4) {
    reasons.push(`OCR confidence ${ocrConfidenceScore} is below 0.40`)
  }
  if (blurScore < 80.0 && faceMatchScore < 65.0) {
    reasons.push(
      `Blur score ${blurScore} is below 80.0 and face match ${faceMatchScore} is below 65.0`
    )
  }

  if (reasons.length > 0) {
    return {
      finalDecision: 'rejected',
      verifiedProbability: 0.0,
      reviewProbability: 0.0,
      rejectedProbability: 1.0,
      decisionBasis: 'placeholder_threshold',
      reasons,
      scores: {
        faceMatchScore,
        livenessScore,
        ocrConfidenceScore,
        blurScore,
        brightnessScore,
        contrastScore,
      },
    }
  }

  // Verified conditions (all must be true)
  const verifiedReasons = []
  const verifiedChecks = [
    {
      ok: faceMatchScore > 80.0,
      pass: `Face match score ${faceMatchScore} is above 80.0`,
      fail: `Face match score ${faceMatchScore} is not above 80.0`,
    },
    {
      ok: livenessScore > 0.75,
      pass: `Liveness score ${livenessScore} is above 0.75`,
      fail: `Liveness score ${livenessScore} is not above 0.75`,
    },
    {
      ok: ocrConfidenceScore > 0.7,
      pass: `OCR confidence ${ocrConfidenceScore} is above 0.70`,
      fail: `OCR confidence ${ocrConfidenceScore} is not above 0.70`,
    },
  ]

  const allVerified = verifiedChecks.every((check) => check.ok)

  if (allVerified) {
    return {
      finalDecision: 'verified',
      verifiedProbability: 1.0,
      reviewProbability: 0.0,
      rejectedProbability: 0.0,
      decisionBasis: 'placeholder_threshold',
      reasons: verifiedChecks.map((check) => check.pass),
      scores: {
        faceMatchScore,
        livenessScore,
        ocrConfidenceScore,
        blurScore,
        brightnessScore,
        contrastScore,
      },
    }
  }

  // Manual review — borderline cases
  for (const check of verifiedChecks) {
    verifiedReasons.push(check.ok ? check.pass : check.fail)
  }
  verifiedReasons.push('Scores fall between rejection and verification thresholds')

  return {
    finalDecision: 'review',
    verifiedProbability: 0.0,
    reviewProbability: 1.0,
    rejectedProbability: 0.0,
    decisionBasis: 'placeholder_threshold',
    reasons: verifiedReasons,
    scores: {
      faceMatchScore,
      livenessScore,
      ocrConfidenceScore,
      blurScore,
      brightnessScore,
      contrastScore,
    },
  }
}

/**
 * Create or update AccessControlRecords for an agent/decision.
 */
export async function enforceAccessDecision(supabase, agentID, decisionID, finalDecision) {
  const accessGranted = finalDecision === 'verified'
  const enforcedAt = new Date().toISOString()

  const { data: existing } = await supabase
    .from('access_control_records')
    .select('*')
    .eq('decision_id', decisionID)
    .maybeSingle()

  if (existing) {
    const { data, error } = await supabase
      .from('access_control_records')
      .update({
        access_granted: accessGranted,
        enforced_at: enforcedAt,
        agent_id: agentID,
      })
      .eq('decision_id', decisionID)
      .select()
      .single()

    if (error) throw new Error(error.message)
    return data
  }

  const { data, error } = await supabase
    .from('access_control_records')
    .insert({
      agent_id: agentID,
      decision_id: decisionID,
      access_granted: accessGranted,
      enforced_at: enforcedAt,
    })
    .select()
    .single()

  if (error) throw new Error(error.message)
  return data
}
