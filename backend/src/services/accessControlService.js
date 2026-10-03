import { getSVMDecision } from './verificationService.js'
import { logAction, ACTIONS, OUTCOMES } from '../utils/auditLogger.js'

/**
 * Accept camelCase (API) or snake_case (verification_scores row) score objects.
 */
function normaliseScores(scores) {
  const fields = {
    faceMatchScore: ['face_match_score', 100],
    livenessScore: ['liveness_score', 1],
    ocrConfidenceScore: ['ocr_confidence_score', 1],
    blurScore: ['blur_score', Infinity],
    brightnessScore: ['brightness_score', 255],
    contrastScore: ['contrast_score', 127.5],
  }
  return Object.fromEntries(Object.entries(fields).map(([name, [alias, maximum]]) => {
    const value = scores?.[name] ?? scores?.[alias]
    if (typeof value !== 'number' || !Number.isFinite(value) || value < 0 || value > maximum) {
      throw new Error(`Missing or invalid verification score: ${name}`)
    }
    return [name, value]
  }))
}

const DECISION_LABELS = { verified: 'Verified', review: 'Manual Review', rejected: 'Rejected' }

function isValidSVMPrediction(result) {
  const probabilities = ['verifiedProbability', 'reviewProbability', 'rejectedProbability']
    .map((key) => result?.[key])
  return (
    result &&
    result.decisionBasis === 'svm_model' &&
    ['verified', 'review', 'rejected'].includes(result.finalDecision) &&
    probabilities.every((value) => typeof value === 'number' && Number.isFinite(value) && value >= 0 && value <= 1) &&
    Math.abs(probabilities.reduce((sum, value) => sum + value, 0) - 1) < 1e-5
  )
}

/**
 * Module 12 KYC decision: the trained SVM classifier, falling back to the
 * Module 8 placeholder thresholds when the SVM is unavailable.
 *
 * @param {object} scores six verification scores (camelCase or snake_case)
 * @param {{ agentID?: string|null, requestID?: string|null }} [context] used for the fallback audit entry
 */
export async function makeKYCDecision(scores, context = {}) {
  const normalised = normaliseScores(scores)

  let fallbackReason
  try {
    const svm = await getSVMDecision(normalised)
    if (svm.available && isValidSVMPrediction(svm)) {
      const probabilities = {
        verified: Number(svm.verifiedProbability),
        review: Number(svm.reviewProbability),
        rejected: Number(svm.rejectedProbability),
      }
      const confidence = (probabilities[svm.finalDecision] * 100).toFixed(1)
      return {
        finalDecision: svm.finalDecision,
        verifiedProbability: probabilities.verified,
        reviewProbability: probabilities.review,
        rejectedProbability: probabilities.rejected,
        decisionBasis: 'svm_model',
        modelVersion: svm.modelVersion || null,
        reasons: [
          `SVM classifier v${svm.modelVersion || 'unknown'} predicted ${DECISION_LABELS[svm.finalDecision]} with ${confidence}% probability`,
        ],
        scores: normalised,
      }
    }
    fallbackReason = svm.available ? 'SVM returned an invalid prediction' : svm.reason
  } catch (err) {
    fallbackReason = err.message
  }

  console.warn(`[KYC] SVM unavailable — placeholder threshold used: ${fallbackReason}`)
  await logAction({
    agentID: context.agentID ?? null,
    requestID: context.requestID ?? null,
    action: ACTIONS.KYC_DECISION_MADE,
    outcome: OUTCOMES.REVIEW,
    performedBy: 'system',
    details: {
      warning: 'SVM unavailable — placeholder threshold used',
      svmFallback: true,
      reason: fallbackReason,
    },
  })

  return applyPlaceholderDecision(normalised)
}

/**
 * Placeholder threshold access-control rules (Module 8).
 * Used only as the fallback when the SVM classifier is unavailable.
 */
export function applyPlaceholderDecision(scores) {
  const {
    faceMatchScore,
    livenessScore,
    ocrConfidenceScore,
    blurScore,
    brightnessScore,
    contrastScore,
  } = normaliseScores(scores)

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
