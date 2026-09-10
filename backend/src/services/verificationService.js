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
