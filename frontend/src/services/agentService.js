import api from './api.js'
import { getDeviceFingerprint } from '../utils/deviceFingerprint.js'

export async function submitPersonalDetails(data) {
  const { data: response } = await api.post('/api/agent/registration', {
    fullName: data.fullName,
    phoneNumber: data.phoneNumber,
    nationalID: data.nationalID,
    dateOfBirth: data.dateOfBirth,
    deviceFingerprint: data.deviceFingerprint || getDeviceFingerprint(),
  })
  return response
}

export async function checkImageQuality(file, purpose = 'document') {
  const formData = new FormData()
  formData.append('image', file, file.name || 'image.jpg')
  formData.append('purpose', purpose)
  const { data } = await api.post('/api/agent/documents/quality-check', formData)
  return data
}

/**
 * @param {{
 *   documentKind?: 'national_id'|'passport',
 *   documentFront?: File|null,
 *   documentBack?: File|null,
 *   selfieImage?: File|null,
 *   selfieChallenge?: string|null,
 * }} payload
 */
export async function uploadDocuments(payload) {
  const formData = new FormData()
  if (payload.documentKind) {
    formData.append('documentKind', payload.documentKind)
  }
  if (payload.documentFront) {
    formData.append('documentFront', payload.documentFront, payload.documentFront.name || 'documentFront.jpg')
  }
  if (payload.documentBack) {
    formData.append('documentBack', payload.documentBack, payload.documentBack.name || 'documentBack.jpg')
  }
  if (payload.selfieImage) {
    formData.append('selfieImage', payload.selfieImage, payload.selfieImage.name || 'selfie.jpg')
  }
  if (payload.selfieChallenge) {
    formData.append('selfieChallenge', payload.selfieChallenge)
  }

  const { data: response } = await api.post('/api/agent/documents', formData)
  return response
}

export async function getProfile() {
  const { data } = await api.get('/api/agent/profile')
  return data
}

export async function getRegistrationStatus() {
  const { data } = await api.get('/api/agent/registration/status')
  return data
}

export async function getMyAuditLogs() {
  const { data } = await api.get('/api/agent/audit')
  return data
}
