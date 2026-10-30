// A saved verification request marks the first submitted verification attempt,
// including image-quality failures. Do not use browser state or expiring strikes.
export async function requiresDocumentCamera(db, agentId) {
  const { data, error } = await db.from('verification_requests')
    .select('request_id').eq('agent_id', agentId).limit(1)
  if (error) throw new Error('Could not check document capture requirements. Please try again.')
  return Boolean(data?.length)
}

export function documentCaptureError(cameraRequired, files, body = {}) {
  if (!cameraRequired) return null
  // Source metadata enforces the app workflow; it is not camera attestation.
  if ((files.documentFront && body.documentFrontSource !== 'camera')
    || (files.documentBack && body.documentBackSource !== 'camera')
    || files.legacyDocument) {
    return 'On a second or later verification attempt, take a new photo of your document using the camera. File uploads are not allowed.'
  }
  return null
}
