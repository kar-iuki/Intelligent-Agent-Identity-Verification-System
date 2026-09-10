import supabase from '../utils/supabaseClient.js'
import { assessImageQuality } from '../services/verificationService.js'

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

async function writeAuditLog(agentId, requestId, action, outcome) {
  const { error } = await supabase.from('audit_logs').insert({
    agent_id: agentId,
    request_id: requestId,
    action,
    outcome,
  })

  if (error) {
    console.error('Failed to write audit log:', error.message)
  }
}

function storagePathFromFileUrl(fileUrl) {
  if (!fileUrl) return null

  // Already a storage object path: agentId/documents/documentImage.jpg
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

  // Fallback: last path segments after bucket name
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

  // Friendlier copies for common cases
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

export async function initiateVerification(req, res) {
  try {
    const agent = await getAgentForUser(req.user.id)
    if (!agent) {
      return res.status(404).json({ error: 'Agent profile not found' })
    }

    const { data: documents, error: docsError } = await supabase
      .from('documents')
      .select('*')
      .eq('agent_id', agent.agent_id)

    if (docsError) {
      return res.status(500).json({ error: docsError.message })
    }

    const nationalIdDoc = documents?.find((doc) => doc.document_type === 'national_id')
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

    // Create verification request first (updated to rejected on quality failure)
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

      await writeAuditLog(
        agent.agent_id,
        verificationRequest.request_id,
        'image_quality_check',
        `failed: ${failureMessages.join('; ') || 'image quality below threshold'}`
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

    // Placeholder zeros for later pipeline stages (OCR, face match, liveness)
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

    await writeAuditLog(
      agent.agent_id,
      verificationRequest.request_id,
      'image_quality_check',
      'passed'
    )

    return res.status(200).json({
      overallPassed: true,
      message: 'Image quality checks passed. Verification is continuing.',
      requestId: verificationRequest.request_id,
      scores: {
        blurScore,
        brightnessScore,
        contrastScore,
        document: quality.document,
        selfie: quality.selfie,
      },
    })
  } catch (err) {
    console.error('initiateVerification error:', err)
    return res.status(500).json({ error: err.message || 'Verification initiation failed' })
  }
}
