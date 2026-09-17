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
  form.append('registeredName', registeredDetails.name || '')
  form.append('registeredIDNumber', registeredDetails.idNumber || '')
  form.append('registeredDOB', registeredDetails.dateOfBirth || '')

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
