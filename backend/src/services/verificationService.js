const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:5000'

/**
 * Send document + selfie buffers to the Python AI quality endpoint.
 * @param {Buffer} documentFileBuffer
 * @param {Buffer} selfieFileBuffer
 * @param {{ documentFilename?: string, selfieFilename?: string, documentMime?: string, selfieMime?: string }} [options]
 */
export async function assessImageQuality(documentFileBuffer, selfieFileBuffer, options = {}) {
  const form = new FormData()

  const documentBlob = new Blob([documentFileBuffer], {
    type: options.documentMime || 'image/jpeg',
  })
  const selfieBlob = new Blob([selfieFileBuffer], {
    type: options.selfieMime || 'image/jpeg',
  })

  form.append(
    'documentImage',
    documentBlob,
    options.documentFilename || 'document.jpg'
  )
  form.append(
    'selfieImage',
    selfieBlob,
    options.selfieFilename || 'selfie.jpg'
  )
  if (options.documentKind) form.append('documentKind', options.documentKind)

  let response
  try {
    response = await fetch(`${AI_SERVICE_URL}/api/quality/assess`, {
      method: 'POST',
      body: form,
    })
  } catch (err) {
    throw new Error(`AI service unreachable: ${err.message}`)
  }

  const payload = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(payload.error || `AI quality assessment failed (${response.status})`)
  }

  return payload
}

/**
 * Assess a single image via the AI quality endpoint (capture wizard gate).
 * @param {Buffer} imageBuffer
 * @param {{ filename?: string, mime?: string, purpose?: 'document'|'selfie' }} [options]
 */
export async function assessSingleImageQuality(imageBuffer, options = {}) {
  const form = new FormData()
  const blob = new Blob([imageBuffer], {
    type: options.mime || 'image/jpeg',
  })
  form.append('image', blob, options.filename || 'image.jpg')
  form.append('purpose', options.purpose || 'document')
  if (options.documentKind) form.append('documentKind', options.documentKind)

  let response
  try {
    response = await fetch(`${AI_SERVICE_URL}/api/quality/assess-single`, {
      method: 'POST',
      body: form,
    })
  } catch (err) {
    throw new Error(`AI service unreachable: ${err.message}`)
  }

  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(payload.error || `AI quality assessment failed (${response.status})`)
  }
  return payload
}

/**
 * Send document image + registered agent details to the Python OCR endpoint.
 *
 * @param {Buffer} documentFileBuffer
 * @param {{ name: string, idNumber: string, dateOfBirth?: string }} registeredDetails
 * @param {{ documentFilename?: string, documentMime?: string }} [options]
 */
export async function verifyDocumentOCR(documentFileBuffer, registeredDetails, options = {}) {
  const form = new FormData()

  const documentBlob = new Blob([documentFileBuffer], {
    type: options.documentMime || 'image/jpeg',
  })

  form.append(
    'documentImage',
    documentBlob,
    options.documentFilename || 'document.jpg'
  )
  if (options.backFileBuffer) {
    const backBlob = new Blob([options.backFileBuffer], {
      type: options.backMime || 'image/jpeg',
    })
    form.append(
      'documentBackImage',
      backBlob,
      options.backFilename || 'documentBack.jpg'
    )
  }
  form.append('registeredName', registeredDetails.name || '')
  form.append('registeredIDNumber', registeredDetails.idNumber || '')
  form.append('registeredDOB', registeredDetails.dateOfBirth || '')
  if (options.documentKind) form.append('documentKind', options.documentKind)

  let response
  try {
    response = await fetch(`${AI_SERVICE_URL}/api/ocr/verify`, {
      method: 'POST',
      body: form,
    })
  } catch (err) {
    throw new Error(`AI service unreachable: ${err.message}`)
  }

  const payload = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(payload.error || `OCR verification failed (${response.status})`)
  }

  return payload
}

/**
 * Send document + selfie buffers to the Python face matching endpoint.
 * @param {Buffer} documentFileBuffer
 * @param {Buffer} selfieFileBuffer
 * @param {{ documentFilename?: string, selfieFilename?: string, documentMime?: string, selfieMime?: string }} [options]
 */
export async function verifyFaceMatch(documentFileBuffer, selfieFileBuffer, options = {}) {
  const form = new FormData()

  const documentBlob = new Blob([documentFileBuffer], {
    type: options.documentMime || 'image/jpeg',
  })
  const selfieBlob = new Blob([selfieFileBuffer], {
    type: options.selfieMime || 'image/jpeg',
  })

  form.append(
    'documentImage',
    documentBlob,
    options.documentFilename || 'document.jpg'
  )
  form.append(
    'selfieImage',
    selfieBlob,
    options.selfieFilename || 'selfie.jpg'
  )

  let response
  try {
    response = await fetch(`${AI_SERVICE_URL}/api/face/verify`, {
      method: 'POST',
      body: form,
    })
  } catch (err) {
    throw new Error(`AI service unreachable: ${err.message}`)
  }

  const payload = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(payload.error || `Face matching failed (${response.status})`)
  }

  return payload
}

/**
 * Send selfie buffer to the Python liveness detection endpoint.
 * @param {Buffer} selfieFileBuffer
 * @param {{ selfieFilename?: string, selfieMime?: string }} [options]
 */
export async function detectLiveness(selfieFileBuffer, options = {}) {
  const form = new FormData()

  const selfieBlob = new Blob([selfieFileBuffer], {
    type: options.selfieMime || 'image/jpeg',
  })

  form.append(
    'selfieImage',
    selfieBlob,
    options.selfieFilename || 'selfie.jpg'
  )

  let response
  try {
    response = await fetch(`${AI_SERVICE_URL}/api/liveness/detect`, {
      method: 'POST',
      body: form,
    })
  } catch (err) {
    throw new Error(`AI service unreachable: ${err.message}`)
  }

  const payload = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(payload.error || `Liveness detection failed (${response.status})`)
  }

  return payload
}

const SVM_TIMEOUT_MS = Number(process.env.SVM_TIMEOUT_MS || 5000)
const SVM_FEATURES = [
  'faceMatchScore',
  'livenessScore',
  'ocrConfidenceScore',
  'blurScore',
  'brightnessScore',
  'contrastScore',
]

/**
 * Check whether the SVM model is loaded in the Python AI service.
 * Throws if the AI service cannot be reached.
 * @returns {Promise<{ modelLoaded: boolean, modelVersion: string|null, trainedAt: string|null }>}
 */
export async function getSVMStatus() {
  let response
  try {
    response = await fetch(`${AI_SERVICE_URL}/api/svm/status`, {
      signal: AbortSignal.timeout(SVM_TIMEOUT_MS),
    })
  } catch (err) {
    throw new Error(`AI service unreachable when checking SVM status: ${err.message}`)
  }

  const payload = await response.json().catch(() => ({}))
  return {
    modelLoaded: response.ok && payload.model_loaded === true,
    modelVersion: payload.model_version || null,
    trainedAt: payload.trained_at || null,
  }
}

/**
 * Classify an applicant with the trained SVM (Module 12).
 *
 * Returns `{ available: false, reason }` when the AI service reports the model is not
 * loaded; otherwise `{ available: true, finalDecision, verifiedProbability,
 * reviewProbability, rejectedProbability, decisionBasis, modelVersion }`.
 * Throws when the AI service is unreachable or the prediction request fails.
 *
 * @param {{ faceMatchScore: number, livenessScore: number, ocrConfidenceScore: number,
 *   blurScore: number, brightnessScore: number, contrastScore: number }} scores
 */
export async function getSVMDecision(scores) {
  const status = await getSVMStatus()
  if (!status.modelLoaded) {
    return {
      available: false,
      reason: 'SVM model is not loaded in the AI service',
      modelVersion: status.modelVersion,
    }
  }

  const body = {}
  for (const name of SVM_FEATURES) {
    if (typeof scores[name] !== 'number' || !Number.isFinite(scores[name])) {
      throw new Error(`Missing or invalid verification score: ${name}`)
    }
    body[name] = scores[name]
  }

  let response
  try {
    response = await fetch(`${AI_SERVICE_URL}/api/svm/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(SVM_TIMEOUT_MS),
    })
  } catch (err) {
    throw new Error(`AI service unreachable during SVM prediction: ${err.message}`)
  }

  const payload = await response.json().catch(() => ({}))

  if (response.status === 503) {
    return {
      available: false,
      reason: payload.error || 'SVM model is not loaded in the AI service',
      modelVersion: payload.model_version || status.modelVersion,
    }
  }
  if (!response.ok) {
    const details = Array.isArray(payload.details) ? ` (${payload.details.join('; ')})` : ''
    throw new Error(`SVM prediction failed (${response.status}): ${payload.error || 'unknown error'}${details}`)
  }

  return { available: true, ...payload }
}
