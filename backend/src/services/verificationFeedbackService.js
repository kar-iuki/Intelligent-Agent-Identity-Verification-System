/**
 * Turn pipeline results into agent-facing feedback: plain-language reasons,
 * the scores behind them, and whether the agent may simply try again.
 *
 * A failure is "borderline" when nothing points at a different person or a
 * bad document — scores just landed short of the thresholds, or a field could
 * not be read. Those are worth a retry with better photos. Hard failures
 * (ID number / date of birth read clearly but different, expired document,
 * a face that is nowhere near the document photo) are not.
 */

// Rejection thresholds mirror accessControlService.applyPlaceholderDecision.
export const THRESHOLDS = {
  faceMatch: { reject: 50, verify: 80, hardFail: 35 },
  liveness: { reject: 0.5, verify: 0.75, hardFail: 0.25 },
  ocr: { reject: 0.4, verify: 0.7 },
}

function num(value, fallback = null) {
  const n = Number(value)
  return Number.isFinite(n) ? n : fallback
}

function pct(value) {
  return `${Math.round(num(value, 0))}%`
}

function ratioPct(value) {
  return `${Math.round(num(value, 0) * 100)}%`
}

/** Plain-language reasons for the document (OCR) step. */
export function describeOcr(ocr = {}) {
  const reasons = []
  const hard = []
  const suggestions = new Set()
  if (!ocr || Object.keys(ocr).length === 0) {
    return { reasons, hard, suggestions: [...suggestions] }
  }

  if (ocr.needsRetake) {
    reasons.push('The document photo was too blurry to read.')
    suggestions.add('Retake the document photo in good light and hold the phone still.')
    return { reasons, hard, suggestions: [...suggestions] }
  }

  if (!ocr.documentType) {
    reasons.push('We could not recognise the type of document in the photo.')
    suggestions.add('Make sure the whole document is inside the frame and the text is readable.')
    return { reasons, hard, suggestions: [...suggestions] }
  }

  if (ocr.documentExpired) {
    reasons.push(`The document has expired${ocr.extractedExpiry ? ` (expiry ${ocr.extractedExpiry})` : ''}.`)
    hard.push('document_expired')
  }

  const missing = []
  if (!ocr.extractedName) missing.push('name')
  if (!ocr.extractedIDNumber) missing.push('ID number')
  if (!ocr.extractedDOB) missing.push('date of birth')
  if (missing.length) {
    reasons.push(`We could not read the ${missing.join(', ')} from the document.`)
    suggestions.add('Retake the document photo closer, in good light, with no glare on the text.')
  }

  if (ocr.extractedName && ocr.nameMatch === false) {
    reasons.push(`The name on the document ("${ocr.extractedName}") does not match the name you registered.`)
    // a name-only mismatch is usually an OCR misread; with ID and DOB also wrong it is not
    if (ocr.idMatch === false && ocr.extractedIDNumber) hard.push('name_and_id_mismatch')
    else suggestions.add('Check that the name on your profile is exactly as printed on the document.')
  }
  if (ocr.extractedIDNumber && ocr.idMatch === false) {
    reasons.push(`The ID number on the document (${ocr.extractedIDNumber}) does not match the ID number you registered.`)
    hard.push('id_mismatch')
  }
  if (ocr.extractedDOB && ocr.dobMatch === false) {
    reasons.push(`The date of birth on the document (${ocr.extractedDOB}) does not match the date of birth you registered.`)
    hard.push('dob_mismatch')
  }
  if (ocr.frontBackMatch === false) {
    reasons.push('The ID number on the back of the card could not be matched to the front.')
    suggestions.add('Retake the back of the ID so the bottom lines of text (the <<< zone) are sharp.')
  }
  if (ocr.lowResolution) {
    suggestions.add('Hold the document closer to the camera so it fills most of the frame.')
  }

  if (reasons.length === 0 && ocr.rejectReason && ocr.matched === false) {
    reasons.push(ocr.rejectReason)
  }
  return { reasons, hard, suggestions: [...suggestions] }
}

/** Plain-language reasons for face match and liveness. */
export function describeBiometrics({ faceMatchScore, livenessScore, faceMatch = {}, liveness = {} }) {
  const reasons = []
  const hard = []
  const suggestions = new Set()
  const face = num(faceMatchScore)
  const live = num(livenessScore)

  if (face !== null && face < THRESHOLDS.faceMatch.reject) {
    reasons.push(`Your selfie did not match the photo on the document closely enough (${pct(face)} similarity, ${THRESHOLDS.faceMatch.reject}% needed).`)
    if (face < THRESHOLDS.faceMatch.hardFail) hard.push('face_mismatch')
    else suggestions.add('Retake the selfie facing the camera directly, without glasses or a hat, in even lighting.')
  } else if (face !== null && face < THRESHOLDS.faceMatch.verify) {
    reasons.push(`Your selfie matched the document photo, but not strongly (${pct(face)} similarity, ${THRESHOLDS.faceMatch.verify}% needed for automatic approval).`)
    suggestions.add('A clearer, well-lit selfie usually raises this score.')
  }
  if (faceMatch?.error) {
    reasons.push(`Face comparison could not be completed: ${faceMatch.error}`)
  }

  if (live !== null && live < THRESHOLDS.liveness.reject) {
    reasons.push(`The liveness check did not pass (${ratioPct(live)} confidence that a live person was in front of the camera).`)
    if (live < THRESHOLDS.liveness.hardFail) hard.push('liveness_fail')
    else suggestions.add('Do the liveness step in a bright room, with your whole face inside the ring.')
  } else if (live !== null && live < THRESHOLDS.liveness.verify) {
    reasons.push(`The liveness check passed, but with low confidence (${ratioPct(live)}).`)
  }
  if (liveness?.error) {
    reasons.push(`Liveness detection could not be completed: ${liveness.error}`)
  }
  return { reasons, hard, suggestions: [...suggestions] }
}

/**
 * Build the feedback block returned to the agent.
 * @param {object} args
 * @param {'verified'|'review'|'rejected'|null} args.finalDecision
 * @param {object} args.scores  { ocrConfidenceScore, faceMatchScore, livenessScore, blurScore, ... }
 * @param {object} args.ocr     OCR result (as returned by the AI service / stored in the audit log)
 * @param {object} args.faceMatch
 * @param {object} args.liveness
 * @param {number} args.strikeCount
 * @param {number} args.maxStrikes
 */
export function buildAgentFeedback({
  finalDecision = null,
  scores = {},
  ocr = {},
  faceMatch = {},
  liveness = {},
  strikeCount = 0,
  maxStrikes = 3,
}) {
  const ocrPart = describeOcr(ocr)
  const bioPart = describeBiometrics({
    faceMatchScore: scores.faceMatchScore ?? faceMatch.faceMatchScore,
    livenessScore: scores.livenessScore ?? liveness.livenessScore,
    faceMatch,
    liveness,
  })

  const reasons = [...ocrPart.reasons, ...bioPart.reasons]
  const hard = [...ocrPart.hard, ...bioPart.hard]
  const suggestions = [...new Set([...ocrPart.suggestions, ...bioPart.suggestions])]

  const ocrScore = num(scores.ocrConfidenceScore ?? ocr.confidenceScore, 0)
  const rejected = finalDecision === 'rejected'
  const borderline = rejected && hard.length === 0
  const attemptsRemaining = Math.max(0, num(maxStrikes, 3) - num(strikeCount, 0))
  const canRetry = borderline && attemptsRemaining > 0

  let summary = null
  if (finalDecision === 'verified') {
    summary = 'All checks passed.'
  } else if (finalDecision === 'review') {
    summary = 'Your scores were not high enough for automatic approval, so an administrator will review your case.'
  } else if (rejected && canRetry) {
    summary = 'Verification did not pass, but nothing indicates a wrong document or person, so you can try again with better photos.'
  } else if (rejected && borderline) {
    summary = 'Verification did not pass and you have used all automatic attempts. Please contact support.'
  } else if (rejected) {
    summary = 'Verification did not pass because the details on the document do not match your registration.'
  }

  return {
    summary,
    reasons,
    suggestions,
    hardFailures: hard,
    borderline,
    canRetry,
    attemptsRemaining,
    maxAttempts: num(maxStrikes, 3),
    scores: {
      ocrConfidenceScore: ocrScore,
      faceMatchScore: num(scores.faceMatchScore ?? faceMatch.faceMatchScore),
      livenessScore: num(scores.livenessScore ?? liveness.livenessScore),
      blurScore: num(scores.blurScore),
    },
    thresholds: THRESHOLDS,
    document: ocr && ocr.documentType
      ? {
          documentType: ocr.documentType,
          extractedName: ocr.extractedName ?? null,
          extractedIDNumber: ocr.extractedIDNumber ?? null,
          extractedDOB: ocr.extractedDOB ?? null,
          extractedExpiry: ocr.extractedExpiry ?? ocr.dateOfExpiry ?? null,
          nameMatch: ocr.nameMatch ?? null,
          idMatch: ocr.idMatch ?? null,
          dobMatch: ocr.dobMatch ?? null,
          frontBackMatch: ocr.frontBackMatch ?? null,
        }
      : null,
  }
}
