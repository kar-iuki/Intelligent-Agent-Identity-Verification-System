import api from './api.js'
import { getDeviceFingerprint } from '../utils/deviceFingerprint.js'

export async function initiateVerification(deviceFingerprint) {
  try {
    const { data } = await api.post('/api/verification/initiate', {
      deviceFingerprint: deviceFingerprint || getDeviceFingerprint(),
    })
    return data
  } catch (err) {
    if (err.response?.status === 422 && err.response.data) {
      return err.response.data
    }
    throw err
  }
}

export async function getVerificationStatus() {
  const { data } = await api.get('/api/verification/status')
  return data
}

export async function getVerificationResult() {
  const { data } = await api.get('/api/verification/result')
  return data
}
