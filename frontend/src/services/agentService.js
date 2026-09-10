import api from './api.js'

export async function submitPersonalDetails(data) {
  const { data: response } = await api.post('/api/agent/registration', {
    fullName: data.fullName,
    phoneNumber: data.phoneNumber,
    nationalID: data.nationalID,
  })
  return response
}

export async function uploadDocuments(documentFile, selfieFile) {
  const formData = new FormData()
  formData.append('documentImage', documentFile)
  formData.append('selfieImage', selfieFile)

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
