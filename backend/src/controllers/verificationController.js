import supabase from '../utils/supabaseClient.js'
import {
  assessImageQuality,
  verifyDocumentOCR,
  verifyFaceMatch,
  detectLiveness,
} from '../services/verificationService.js'
import {
  applyPlaceholderDecision,
  enforceAccessDecision,
} from '../services/accessControlService.js'
import { logAction, ACTIONS, OUTCOMES, scoreToOutcome } from '../utils/auditLogger.js'
import { recordStrike } from '../services/strikeService.js'

const BUCKET = 'agent-documents'

async function getAgentForUser(userId) {
  const { data, error } = await supabase
    .from('agents')
    .select('*')
    .eq('user_id', userId)
    .single()

  if (error || !data) return null
  return data
}

function storagePathFromFileUrl(fileUrl) {
  if (!fileUrl) return null

  if (!fileUrl.startsWith('http')) {
    return fileUrl
  }

  const marker = `/object/public/${BUCKET}/`
  const privateMarker = `/object/sign/${BUCKET}/`
  const authenticatedMarker = `/object/authenticated/${BUCKET}/`

  for (const m of [marker, privateMarker, authenticatedMarker]) {
    const index = fileUrl.indexOf(m)
    if (index !== -1) {
      return decodeURIComponent(fileUrl.slice(index + m.length).split('?')[0])
    }
  }

  const parts = fileUrl.split(`${BUCKET}/`)
  if (parts.length > 1) {
    return decodeURIComponent(parts[1].split('?')[0])
  }

  return fileUrl
}

function mimeFromPath(path) {
  return path?.toLowerCase().endsWith('.png') ? 'image/png' : 'image/jpeg'
}

function average(a, b) {
  return Number(((Number(a) + Number(b)) / 2).toFixed(4))
}

function buildFailureMessages(quality) {
  const messages = []

  for (const failure of quality.document?.failures || []) {
    messages.push(`Your document image: ${failure.replace(/^Image /, '').toLowerCase()}`)
  }
  for (const failure of quality.selfie?.failures || []) {
    messages.push(`Your selfie: ${failure.replace(/^Image /, '').toLowerCase()}`)
  }

  return messages.map((msg) => {
    if (msg.includes('too blurry')) {
      return msg.includes('selfie')
        ? 'Your selfie is too blurry'
        : 'Your document image is too blurry'
    }
    if (msg.includes('too dark')) {
      return msg.includes('selfie')
        ? 'Your selfie is too dark'
        : 'Your document image is too dark'
    }
    if (msg.includes('too bright')) {
      return msg.includes('selfie')
        ? 'Your selfie is too bright'
        : 'Your document image is too bright'
    }
    if (msg.includes('low contrast')) {
      return msg.includes('selfie')
        ? 'Your selfie has low contrast'
        : 'Your document image has low contrast'
    }
    return msg
  })
}

/**
 * Run OCR after image quality passes. Updates scores / review status,
 * writes audit log, and always continues the pipeline.
 */
export async function runOCRVerification({
  agent,
  verificationRequest,
  documentBuffer,
  documentPath,
}) {
  const ocrResult = await verifyDocumentOCR(
    documentBuffer,
    {
      name: agent.full_name,
      idNumber: agent.national_id,
      dateOfBirth: agent.date_of_birth || '',
    },
    {
      documentFilename: documentPath.split('/').pop(),
      documentMime: mimeFromPath(documentPath),
    }
  )

  const confidenceScore = Number(ocrResult.confidenceScore ?? 0)

  const { error: scoreUpdateError } = await supabase
    .from('verification_scores')
    .update({ ocr_confidence_score: confidenceScore })
    .eq('request_id', verificationRequest.request_id)

  if (scoreUpdateError) {
    throw new Error(scoreUpdateError.message)
  }

  const lowConfidence = !ocrResult.matched && confidenceScore < 0.4
  const ocrOutcome = scoreToOutcome(confidenceScore, 0.7, 0.4)

  if (lowConfidence) {
    const { error: statusError } = await supabase
      .from('verification_requests')
      .update({ status: 'review' })
      .eq('request_id', verificationRequest.request_id)

    if (statusError) {
      throw new Error(statusError.message)
    }
  }

  await logAction({
    agentID: agent.agent_id,
    requestID: verificationRequest.request_id,
    action: ACTIONS.OCR_VERIFIED,
    outcome: ocrOutcome,
    performedBy: 'system',
    details: {
      confidenceScore,
      matched: Boolean(ocrResult.matched),
      nameMatch: Boolean(ocrResult.nameMatch),
      idMatch: Boolean(ocrResult.idMatch),
      dobMatch: Boolean(ocrResult.dobMatch),
      flaggedForReview: lowConfidence,
      extractedName: ocrResult.extractedName ?? null,
      extractedIDNumber: ocrResult.extractedIDNumber ?? null,
      extractedDOB: ocrResult.extractedDOB ?? null,
      registeredName: agent.full_name ?? null,
      registeredIDNumber: agent.national_id ?? null,
      registeredDOB: agent.date_of_birth ?? null,
      rawText: Array.isArray(ocrResult.rawText) ? ocrResult.rawText.slice(0, 40) : [],
    },
  })

  return {
    ...ocrResult,
    confidenceScore,
    flaggedForReview: lowConfidence,
  }
}

/**
 * Run face matching after OCR. Updates face_match_score, writes audit log,
 * and always continues the pipeline.
 */
export async function runFaceMatchVerification({
  agent,
  verificationRequest,
  documentBuffer,
  selfieBuffer,
  documentPath,
  selfiePath,
}) {
  const faceResult = await verifyFaceMatch(documentBuffer, selfieBuffer, {
    documentFilename: documentPath.split('/').pop(),
    selfieFilename: selfiePath.split('/').pop(),
    documentMime: mimeFromPath(documentPath),
    selfieMime: mimeFromPath(selfiePath),
  })

  const faceMatchScore = Number(faceResult.faceMatchScore ?? 0)
  const documentFaceDetected = Boolean(faceResult.documentFaceDetected)
  const selfieFaceDetected = Boolean(faceResult.selfieFaceDetected)

  const { error: scoreUpdateError } = await supabase
    .from('verification_scores')
    .update({ face_match_score: faceMatchScore })
    .eq('request_id', verificationRequest.request_id)

  if (scoreUpdateError) {
    throw new Error(scoreUpdateError.message)
  }

  if (!documentFaceDetected || !selfieFaceDetected) {
    const missing = []
    if (!documentFaceDetected) missing.push('document')
    if (!selfieFaceDetected) missing.push('selfie')

    await logAction({
      agentID: agent.agent_id,
      requestID: verificationRequest.request_id,
      action: ACTIONS.FACE_MATCH_COMPLETED,
      outcome: OUTCOMES.FAILED,
      performedBy: 'system',
      details: {
        faceMatchScore: 0,
        missing,
        message: faceResult.message || 'No face detected',
      },
    })
  } else {
    await logAction({
      agentID: agent.agent_id,
      requestID: verificationRequest.request_id,
      action: ACTIONS.FACE_MATCH_COMPLETED,
      outcome: scoreToOutcome(faceMatchScore, 80, 50),
      performedBy: 'system',
      details: {
        faceMatchScore,
        matched: Boolean(faceResult.matched),
        documentFaceDetected: true,
        selfieFaceDetected: true,
      },
    })
  }

  return {
    ...faceResult,
    faceMatchScore,
  }
}

/**
 * Run liveness detection after face matching. Updates liveness_score,
 * writes audit log, and continues to the placeholder access decision.
 */
export async function runLivenessDetection({
  agent,
  verificationRequest,
  selfieBuffer,
  selfiePath,
}) {
  const livenessResult = await detectLiveness(selfieBuffer, {
    selfieFilename: selfiePath.split('/').pop(),
    selfieMime: mimeFromPath(selfiePath),
  })

  const livenessScore = Number(livenessResult.livenessScore ?? 0)

  const { error: scoreUpdateError } = await supabase
    .from('verification_scores')
    .update({ liveness_score: livenessScore })
    .eq('request_id', verificationRequest.request_id)

  if (scoreUpdateError) {
    throw new Error(scoreUpdateError.message)
  }

  await logAction({
    agentID: agent.agent_id,
    requestID: verificationRequest.request_id,
    action: ACTIONS.LIVENESS_DETECTED,
    outcome: scoreToOutcome(livenessScore, 0.75, 0.5),
    performedBy: 'system',
    details: {
      livenessScore,
      classification: livenessResult.classification,
      isLive: Boolean(livenessResult.isLive),
    },
  })

  return {
    ...livenessResult,
    livenessScore,
  }
}

/**
 * Module 8 access decision using placeholder thresholds.
 * Replaced by the trained SVM in Module 12.
 */
export async function makeAccessDecision({
  agent,
  verificationRequest,
  ipAddress = null,
  deviceFingerprint = null,
}) {
  const { data: scores, error: scoresError } = await supabase
    .from('verification_scores')
    .select('*')
    .eq('request_id', verificationRequest.request_id)
    .single()

  if (scoresError || !scores) {
    throw new Error(scoresError?.message || 'Verification scores not found')
  }

  const decisionResult = applyPlaceholderDecision(scores)

  const { data: existingDecision } = await supabase
    .from('kyc_decisions')
    .select('*')
    .eq('request_id', verificationRequest.request_id)
    .maybeSingle()

  let decision
  if (existingDecision) {
    const { data, error } = await supabase
      .from('kyc_decisions')
      .update({
        final_decision: decisionResult.finalDecision,
        verified_probability: decisionResult.verifiedProbability,
        review_probability: decisionResult.reviewProbability,
        rejected_probability: decisionResult.rejectedProbability,
        decision_basis: decisionResult.decisionBasis,
        decided_at: new Date().toISOString(),
      })
      .eq('request_id', verificationRequest.request_id)
      .select()
      .single()

    if (error) throw new Error(error.message)
    decision = data
  } else {
    const { data, error } = await supabase
      .from('kyc_decisions')
      .insert({
        request_id: verificationRequest.request_id,
        final_decision: decisionResult.finalDecision,
        verified_probability: decisionResult.verifiedProbability,
        review_probability: decisionResult.reviewProbability,
        rejected_probability: decisionResult.rejectedProbability,
        decision_basis: decisionResult.decisionBasis,
        decided_at: new Date().toISOString(),
      })
      .select()
      .single()

    if (error) throw new Error(error.message)
    decision = data
  }

  const access = await enforceAccessDecision(
    supabase,
    agent.agent_id,
    decision.decision_id,
    decisionResult.finalDecision
  )

  const { error: statusError } = await supabase
    .from('verification_requests')
    .update({ status: decisionResult.finalDecision })
    .eq('request_id', verificationRequest.request_id)

  if (statusError) {
    throw new Error(statusError.message)
  }

  const decisionOutcome =
    decisionResult.finalDecision === 'verified'
      ? OUTCOMES.VERIFIED
      : decisionResult.finalDecision === 'review'
        ? OUTCOMES.REVIEW
        : OUTCOMES.REJECTED

  await logAction({
    agentID: agent.agent_id,
    requestID: verificationRequest.request_id,
    action: ACTIONS.KYC_DECISION_MADE,
    outcome: decisionOutcome,
    performedBy: 'system',
    details: {
      decision: decisionResult.finalDecision,
      basis: decisionResult.decisionBasis,
      reasons: decisionResult.reasons,
      decisionId: decision.decision_id,
    },
  })

  if (decisionResult.finalDecision === 'review') {
    await logAction({
      agentID: agent.agent_id,
      requestID: verificationRequest.request_id,
      action: ACTIONS.MANUAL_REVIEW_FLAGGED,
      outcome: OUTCOMES.REVIEW,
      performedBy: 'system',
      details: {
        reasons: decisionResult.reasons,
      },
    })
  } else {
    await logAction({
      agentID: agent.agent_id,
      requestID: verificationRequest.request_id,
      action: access.access_granted ? ACTIONS.ACCESS_GRANTED : ACTIONS.ACCESS_DENIED,
      outcome: access.access_granted ? OUTCOMES.SUCCESS : OUTCOMES.REJECTED,
      performedBy: 'system',
      ipAddress,
      deviceFingerprint,
      details: {
        accessGranted: Boolean(access.access_granted),
        decision: decisionResult.finalDecision,
      },
    })
  }

  if (decisionResult.finalDecision === 'rejected') {
    await recordStrike(
      agent.agent_id,
      ipAddress,
      deviceFingerprint,
      `access_decision_rejected: ${(decisionResult.reasons || []).join(' | ') || 'threshold failure'}`
    )
  }

  return {
    ...decisionResult,
    decisionId: decision.decision_id,
    access,
    decision,
  }
}

/** @deprecated Use makeAccessDecision */
export async function makePlaceholderAccessDecision(args) {
  return makeAccessDecision(args)
}

export async function getVerificationStatus(req, res) {
  try {
    const agent = await getAgentForUser(req.user.id)
    if (!agent) {
      return res.status(404).json({ error: 'Agent profile not found' })
    }

    const { data: request } = await supabase
      .from('verification_requests')
      .select('*')
      .eq('agent_id', agent.agent_id)
      .order('created_at', { ascending: false })
      .limit(1)
      .maybeSingle()

    if (!request) {
      return res.json({
        status: 'not_started',
        pipeline: {
          imageQuality: 'pending',
          documentVerification: 'pending',
          faceMatching: 'pending',
          livenessDetection: 'pending',
          verificationDecision: 'pending',
        },
        scores: null,
        decision: null,
      })
    }

    const [{ data: scores }, { data: decision }, { data: access }] = await Promise.all([
      supabase
        .from('verification_scores')
        .select('*')
        .eq('request_id', request.request_id)
        .maybeSingle(),
      supabase
        .from('kyc_decisions')
        .select('*')
        .eq('request_id', request.request_id)
        .maybeSingle(),
      supabase
        .from('access_control_records')
        .select('*')
        .eq('agent_id', agent.agent_id)
        .order('enforced_at', { ascending: false })
        .limit(1)
        .maybeSingle(),
    ])

    const hasScores = Boolean(scores)
    const pipeline = {
      imageQuality: hasScores ? 'complete' : 'pending',
      documentVerification:
        hasScores && Number(scores.ocr_confidence_score) > 0 ? 'complete' : hasScores ? 'complete' : 'pending',
      faceMatching:
        hasScores && Number(scores.face_match_score) > 0 ? 'complete' : hasScores ? 'complete' : 'pending',
      livenessDetection:
        hasScores && Number(scores.liveness_score) > 0 ? 'complete' : hasScores ? 'complete' : 'pending',
      verificationDecision: decision ? 'complete' : 'pending',
    }

    // If scores row exists, quality+later steps were attempted
    if (hasScores) {
      pipeline.imageQuality = 'complete'
      pipeline.documentVerification = 'complete'
      pipeline.faceMatching = 'complete'
      pipeline.livenessDetection = 'complete'
    }

    const finalStatuses = ['verified', 'review', 'rejected']
    const isFinal = finalStatuses.includes(request.status) && Boolean(decision)

    return res.json({
      status: request.status,
      isFinal,
      requestId: request.request_id,
      pipeline,
      scores: scores
        ? {
            blurScore: scores.blur_score,
            brightnessScore: scores.brightness_score,
            contrastScore: scores.contrast_score,
            ocrConfidenceScore: scores.ocr_confidence_score,
            faceMatchScore: scores.face_match_score,
            livenessScore: scores.liveness_score,
          }
        : null,
      decision: decision
        ? {
            finalDecision: decision.final_decision,
            decisionBasis: decision.decision_basis || 'placeholder_threshold',
            verifiedProbability: decision.verified_probability,
            reviewProbability: decision.review_probability,
            rejectedProbability: decision.rejected_probability,
            decidedAt: decision.decided_at,
          }
        : null,
      access: access
        ? {
            accessGranted: access.access_granted,
            enforcedAt: access.enforced_at,
          }
        : null,
    })
  } catch (err) {
    return res.status(500).json({ error: err.message })
  }
}

export async function getVerificationResult(req, res) {
  try {
    const agent = await getAgentForUser(req.user.id)
    if (!agent) {
      return res.status(404).json({ error: 'Agent profile not found' })
    }

    const { data: request } = await supabase
      .from('verification_requests')
      .select('*')
      .eq('agent_id', agent.agent_id)
      .order('created_at', { ascending: false })
      .limit(1)
      .maybeSingle()

    if (!request) {
      return res.status(404).json({ error: 'No verification request found' })
    }

    const { data: decision } = await supabase
      .from('kyc_decisions')
      .select('*')
      .eq('request_id', request.request_id)
      .maybeSingle()

    if (!decision) {
      return res.status(404).json({ error: 'No decision has been made yet' })
    }

    const { data: access } = await supabase
      .from('access_control_records')
      .select('*')
      .eq('decision_id', decision.decision_id)
      .maybeSingle()

    const { data: scores } = await supabase
      .from('verification_scores')
      .select('*')
      .eq('request_id', request.request_id)
      .maybeSingle()

    return res.json({
      request,
      decision,
      access,
      scores,
    })
  } catch (err) {
    return res.status(500).json({ error: err.message })
  }
}

export async function initiateVerification(req, res) {
  try {
    const agent = await getAgentForUser(req.user.id)
    if (!agent) {
      return res.status(404).json({ error: 'Agent profile not found' })
    }

    const deviceFingerprint = req.body?.deviceFingerprint
      ? String(req.body.deviceFingerprint)
      : req.deviceFingerprint || null
    const ipAddress = req.clientIP || null

    const { data: documents, error: docsError } = await supabase
      .from('documents')
      .select('*')
      .eq('agent_id', agent.agent_id)

    if (docsError) {
      return res.status(500).json({ error: docsError.message })
    }

    const nationalIdDoc =
      documents?.find((doc) => doc.document_type === 'national_id')
      || documents?.find((doc) => doc.document_type === 'id_front')
      || documents?.find((doc) => doc.document_type === 'passport')
    const selfieDoc = documents?.find((doc) => doc.document_type === 'selfie')

    if (!nationalIdDoc || !selfieDoc) {
      return res.status(400).json({
        error: 'Both identity document and selfie must be uploaded before verification',
      })
    }

    const documentPath = storagePathFromFileUrl(nationalIdDoc.file_url)
    const selfiePath = storagePathFromFileUrl(selfieDoc.file_url)

    const { data: documentBlob, error: documentDownloadError } = await supabase.storage
      .from(BUCKET)
      .download(documentPath)

    if (documentDownloadError || !documentBlob) {
      return res.status(500).json({
        error: documentDownloadError?.message || 'Failed to download document image',
      })
    }

    const { data: selfieBlob, error: selfieDownloadError } = await supabase.storage
      .from(BUCKET)
      .download(selfiePath)

    if (selfieDownloadError || !selfieBlob) {
      return res.status(500).json({
        error: selfieDownloadError?.message || 'Failed to download selfie image',
      })
    }

    const documentBuffer = Buffer.from(await documentBlob.arrayBuffer())
    const selfieBuffer = Buffer.from(await selfieBlob.arrayBuffer())

    let quality
    try {
      quality = await assessImageQuality(documentBuffer, selfieBuffer, {
        documentFilename: documentPath.split('/').pop(),
        selfieFilename: selfiePath.split('/').pop(),
        documentMime: mimeFromPath(documentPath),
        selfieMime: mimeFromPath(selfiePath),
      })
    } catch (err) {
      return res.status(503).json({ error: err.message })
    }

    const { data: verificationRequest, error: requestError } = await supabase
      .from('verification_requests')
      .insert({
        agent_id: agent.agent_id,
        document_id: nationalIdDoc.document_id,
        status: quality.overallPassed ? 'pending' : 'rejected',
      })
      .select()
      .single()

    if (requestError || !verificationRequest) {
      return res.status(500).json({
        error: requestError?.message || 'Failed to create verification request',
      })
    }

    await logAction({
      agentID: agent.agent_id,
      requestID: verificationRequest.request_id,
      action: ACTIONS.VERIFICATION_INITIATED,
      outcome: quality.overallPassed ? OUTCOMES.SUCCESS : OUTCOMES.FAILED,
      performedBy: req.user.id,
      ipAddress,
      deviceFingerprint,
      details: {
        documentId: nationalIdDoc.document_id,
        qualityPassed: Boolean(quality.overallPassed),
        deviceFingerprint,
      },
    })

    if (!quality.overallPassed) {
      const failureMessages = buildFailureMessages(quality)
      const failedImages = []
      if (!quality.document?.passed) failedImages.push('document')
      if (!quality.selfie?.passed) failedImages.push('selfie')

      const { data: decision, error: decisionError } = await supabase
        .from('kyc_decisions')
        .insert({
          request_id: verificationRequest.request_id,
          final_decision: 'rejected',
          verified_probability: 0,
          review_probability: 0,
          rejected_probability: 1,
          decision_basis: 'image_quality_failure',
        })
        .select()
        .single()

      if (decisionError) {
        return res.status(500).json({ error: decisionError.message })
      }

      const { error: accessError } = await supabase
        .from('access_control_records')
        .insert({
          agent_id: agent.agent_id,
          decision_id: decision.decision_id,
          access_granted: false,
        })

      if (accessError) {
        return res.status(500).json({ error: accessError.message })
      }

      await logAction({
        agentID: agent.agent_id,
        requestID: verificationRequest.request_id,
        action: ACTIONS.IMAGE_QUALITY_ASSESSED,
        outcome: OUTCOMES.FAILED,
        performedBy: 'system',
        ipAddress,
        deviceFingerprint,
        details: {
          failures: failureMessages,
          failedImages,
          document: quality.document,
          selfie: quality.selfie,
        },
      })

      await logAction({
        agentID: agent.agent_id,
        requestID: verificationRequest.request_id,
        action: ACTIONS.KYC_DECISION_MADE,
        outcome: OUTCOMES.REJECTED,
        performedBy: 'system',
        details: { reason: 'image_quality_failure' },
      })

      await logAction({
        agentID: agent.agent_id,
        requestID: verificationRequest.request_id,
        action: ACTIONS.ACCESS_DENIED,
        outcome: OUTCOMES.REJECTED,
        performedBy: 'system',
        details: { accessGranted: false },
      })

      await recordStrike(
        agent.agent_id,
        ipAddress,
        deviceFingerprint,
        `image_quality_failure: ${failureMessages.join('; ') || 'below threshold'}`
      )

      return res.status(422).json({
        overallPassed: false,
        failedImages,
        failures: failureMessages,
        document: quality.document,
        selfie: quality.selfie,
        message: 'Image quality checks failed. Please re-upload clearer images.',
        note: 'Rejected due to image quality failure',
        requestId: verificationRequest.request_id,
      })
    }

    const blurScore = average(quality.document.blurScore, quality.selfie.blurScore)
    const brightnessScore = average(
      quality.document.brightnessScore,
      quality.selfie.brightnessScore
    )
    const contrastScore = average(
      quality.document.contrastScore,
      quality.selfie.contrastScore
    )

    const { error: scoresError } = await supabase
      .from('verification_scores')
      .insert({
        request_id: verificationRequest.request_id,
        face_match_score: 0,
        liveness_score: 0,
        ocr_confidence_score: 0,
        blur_score: blurScore,
        brightness_score: brightnessScore,
        contrast_score: contrastScore,
      })

    if (scoresError) {
      return res.status(500).json({ error: scoresError.message })
    }

    await logAction({
      agentID: agent.agent_id,
      requestID: verificationRequest.request_id,
      action: ACTIONS.IMAGE_QUALITY_ASSESSED,
      outcome: OUTCOMES.PASSED,
      performedBy: 'system',
      ipAddress: req.clientIP,
      details: {
        blurScore,
        brightnessScore,
        contrastScore,
      },
    })

    // Pipeline step 2: OCR document verification (continues regardless of match)
    let ocrResult
    try {
      ocrResult = await runOCRVerification({
        agent,
        verificationRequest,
        documentBuffer,
        documentPath,
      })
    } catch (err) {
      return res.status(503).json({
        error: err.message || 'OCR verification failed',
        overallPassed: true,
        qualityPassed: true,
        ocrCompleted: false,
        faceMatchCompleted: false,
        requestId: verificationRequest.request_id,
      })
    }

    // Pipeline step 3: biometric face matching (continues regardless of score)
    let faceResult
    try {
      faceResult = await runFaceMatchVerification({
        agent,
        verificationRequest,
        documentBuffer,
        selfieBuffer,
        documentPath,
        selfiePath,
      })
    } catch (err) {
      return res.status(503).json({
        error: err.message || 'Face matching failed',
        overallPassed: true,
        qualityPassed: true,
        ocrCompleted: true,
        faceMatchCompleted: false,
        livenessCompleted: false,
        requestId: verificationRequest.request_id,
        ocr: ocrResult,
      })
    }

    // Pipeline step 4: liveness detection
    let livenessResult
    try {
      livenessResult = await runLivenessDetection({
        agent,
        verificationRequest,
        selfieBuffer,
        selfiePath,
      })
    } catch (err) {
      return res.status(503).json({
        error: err.message || 'Liveness detection failed',
        overallPassed: true,
        qualityPassed: true,
        ocrCompleted: true,
        faceMatchCompleted: true,
        livenessCompleted: false,
        requestId: verificationRequest.request_id,
        ocr: ocrResult,
        faceMatch: faceResult,
      })
    }

    // Placeholder access control decision (Module 8 thresholds; SVM in Module 12)
    let accessDecision
    try {
      accessDecision = await makeAccessDecision({
        agent,
        verificationRequest,
        ipAddress,
        deviceFingerprint,
      })
    } catch (err) {
      return res.status(500).json({
        error: err.message || 'Access control decision failed',
        overallPassed: true,
        qualityPassed: true,
        ocrCompleted: true,
        faceMatchCompleted: true,
        livenessCompleted: true,
        requestId: verificationRequest.request_id,
        ocr: ocrResult,
        faceMatch: faceResult,
        liveness: livenessResult,
      })
    }

    return res.status(200).json({
      overallPassed: true,
      qualityPassed: true,
      ocrCompleted: true,
      faceMatchCompleted: true,
      livenessCompleted: true,
      decisionCompleted: true,
      message: 'Full verification pipeline completed.',
      requestId: verificationRequest.request_id,
      finalDecision: accessDecision.finalDecision,
      scores: {
        blurScore,
        brightnessScore,
        contrastScore,
        ocrConfidenceScore: ocrResult.confidenceScore,
        faceMatchScore: faceResult.faceMatchScore,
        livenessScore: livenessResult.livenessScore,
        document: quality.document,
        selfie: quality.selfie,
      },
      ocr: ocrResult,
      faceMatch: faceResult,
      liveness: livenessResult,
      decision: accessDecision,
      pipeline: {
        imageQuality: 'complete',
        documentVerification: 'complete',
        faceMatching: 'complete',
        livenessDetection: 'complete',
        verificationDecision: 'complete',
      },
    })
  } catch (err) {
    console.error('initiateVerification error:', err)
    return res.status(500).json({ error: err.message || 'Verification initiation failed' })
  }
}
