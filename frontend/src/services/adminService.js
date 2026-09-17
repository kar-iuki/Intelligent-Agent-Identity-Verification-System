import api from './api.js'

export async function getPendingCases() {
  const { data } = await api.get('/api/admin/cases/pending')
  return data
}

export async function getAllAgents(statusFilter) {
  const params = {}
  if (statusFilter) params.status = statusFilter
  const { data } = await api.get('/api/admin/agents', { params })
  return data
}

export async function getAgentDetail(agentID) {
  const { data } = await api.get(`/api/admin/agents/${agentID}`)
  return data
}

export async function getAgentImages(agentID) {
  const { data } = await api.get(`/api/admin/agents/${agentID}/images`)
  return data
}

export async function getAgentAuditLogs(agentID) {
  const { data } = await api.get(`/api/admin/agents/${agentID}/audit`)
  return data
}

export async function getFlaggedRegistrations() {
  const { data } = await api.get('/api/admin/fraud/flagged')
  return data
}

export async function resetAgentStrikes(agentID) {
  const { data } = await api.post(`/api/admin/agents/${agentID}/reset-strikes`)
  return data
}

export async function getDashboardStats() {
  const { data } = await api.get('/api/admin/stats')
  return data
}

export async function getRecentActivity() {
  const { data } = await api.get('/api/admin/activity/recent')
  return data
}

export async function approveAgent(agentID, requestID) {
  const { data } = await api.post(`/api/admin/agents/${agentID}/approve`, {
    requestID,
  })
  return data
}

export async function rejectAgent(agentID, requestID, reason = '') {
  const { data } = await api.post(`/api/admin/agents/${agentID}/reject`, {
    requestID,
    reason,
  })
  return data
}

export async function getAuditLogs(page = 1, pageSize = 20) {
  const { data } = await api.get('/api/admin/audit-logs', {
    params: { page, pageSize },
  })
  return data
}

export async function exportAuditLogs(filters = {}) {
  const response = await api.get('/api/admin/audit/export', {
    params: filters,
    responseType: 'blob',
  })
  return response.data
}
