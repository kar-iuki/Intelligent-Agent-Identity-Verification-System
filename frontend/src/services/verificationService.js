import api from './api.js'

export async function initiateVerification() {
  try {
    const { data } = await api.post('/api/verification/initiate')
    return data
  } catch (err) {
    // Quality failures return 422 with assessment details
    if (err.response?.status === 422 && err.response.data) {
      return err.response.data
    }
    throw err
  }
}
