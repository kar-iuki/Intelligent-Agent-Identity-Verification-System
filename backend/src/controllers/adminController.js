import supabase from '../utils/supabaseClient.js'
import { enforceAccessDecision } from '../services/accessControlService.js'
import { logAction, ACTIONS, OUTCOMES } from '../utils/auditLogger.js'
import { resetStrikes, getStrikeCount } from '../services/strikeService.js'

async function resolvePerformerLabel(performedBy) {
  if (!performedBy || performedBy === 'system') {
    return 'System'
  }

  const { data: userRow } = await supabase
    .from('users')
    .select('email, role')
    .eq('user_id', performedBy)
    .maybeSingle()

  if (!userRow) return performedBy

  const { data: agentRow } = await supabase
    .from('agents')
    .select('full_name')
    .eq('user_id', performedBy)
    .maybeSingle()

  return agentRow?.full_name || userRow.email || performedBy
}

export async function getPendingReviewCases(req, res) {
  try {
    const { data: requests, error } = await supabase
      .from('verification_requests')
      .select('*')
      .eq('status', 'review')
      .order('created_at', { ascending: false })

    if (error) return res.status(500).json({ error: error.message })

    const cases = []
    for (const request of requests || []) {
      const [{ data: agent }, { data: scores }, { data: decision }] = await Promise.all([
        supabase.from('agents').select('*').eq('agent_id', request.agent_id).single(),
        supabase.from('verification_scores').select('*').eq('request_id', request.request_id).maybeSingle(),
        supabase.from('kyc_decisions').select('*').eq('request_id', request.request_id).maybeSingle(),
      ])

      cases.push({
        request,
        agent,
        scores,
        decision,
      })
    }

    return res.json({ cases })
  } catch (err) {
    return res.status(500).json({ error: err.message })
  }
}

export async function getAgentVerificationDetail(req, res) {
  try {
    const { agentID } = req.params

    const { data: agent, error: agentError } = await supabase
      .from('agents')
      .select('*')
      .eq('agent_id', agentID)
      .single()

    if (agentError || !agent) {
      return res.status(404).json({ error: 'Agent not found' })
    }

    const { data: userRow } = await supabase
      .from('users')
      .select('email')
      .eq('user_id', agent.user_id)
      .maybeSingle()

    const { data: requests } = await supabase
      .from('verification_requests')
      .select('*')
      .eq('agent_id', agentID)
      .order('created_at', { ascending: false })

    const history = []
    for (const request of requests || []) {
      const [{ data: scores }, { data: decision }, { data: access }] = await Promise.all([
        supabase.from('verification_scores').select('*').eq('request_id', request.request_id).maybeSingle(),
        supabase.from('kyc_decisions').select('*').eq('request_id', request.request_id).maybeSingle(),
        supabase
          .from('access_control_records')
          .select('*')
          .eq('agent_id', agentID)
          .order('enforced_at', { ascending: false })
          .limit(1)
          .maybeSingle(),
      ])

      history.push({ request, scores, decision, access })
    }

    const { data: auditLogs } = await supabase
      .from('audit_logs')
      .select('*')
      .eq('agent_id', agentID)
      .order('timestamp', { ascending: false })

    const latestOcrLog = (auditLogs || []).find((row) => row.action === 'OCR_VERIFIED')
    const latestOcr = latestOcrLog?.details
      ? {
          timestamp: latestOcrLog.timestamp,
          confidenceScore: latestOcrLog.details.confidenceScore ?? null,
          extractedName: latestOcrLog.details.extractedName ?? null,
          extractedIDNumber: latestOcrLog.details.extractedIDNumber ?? null,
          extractedDOB: latestOcrLog.details.extractedDOB ?? null,
          extractedExpiry: latestOcrLog.details.extractedExpiry ?? null,
          registeredName: latestOcrLog.details.registeredName ?? agent.full_name ?? null,
          registeredIDNumber: latestOcrLog.details.registeredIDNumber ?? agent.national_id ?? null,
          registeredDOB: latestOcrLog.details.registeredDOB ?? agent.date_of_birth ?? null,
          nameMatch: latestOcrLog.details.nameMatch ?? null,
          idMatch: latestOcrLog.details.idMatch ?? null,
          dobMatch: latestOcrLog.details.dobMatch ?? null,
          documentType: latestOcrLog.details.documentType ?? null,
          fieldMatches: latestOcrLog.details.fieldMatches ?? [],
          needsManualReview: latestOcrLog.details.needsManualReview ?? null,
          rejectReason: latestOcrLog.details.rejectReason ?? null,
          rawText: latestOcrLog.details.rawText ?? [],
        }
      : null

    return res.json({
      agent: {
        ...agent,
        email: userRow?.email || null,
      },
      history,
      auditLogs: auditLogs || [],
      latestOcr,
    })
  } catch (err) {
    return res.status(500).json({ error: err.message })
  }
}

export async function approveAgent(req, res) {
  try {
    const { agentID } = req.params
    const { requestID } = req.body

    if (!requestID) {
      return res.status(400).json({ error: 'requestID is required' })
    }

    const { data: decision, error: decisionError } = await supabase
      .from('kyc_decisions')
      .update({
        final_decision: 'verified',
        verified_probability: 1.0,
        review_probability: 0.0,
        rejected_probability: 0.0,
        decided_at: new Date().toISOString(),
      })
      .eq('request_id', requestID)
      .select()
      .single()

    if (decisionError || !decision) {
      return res.status(404).json({ error: decisionError?.message || 'Decision not found' })
    }

    const access = await enforceAccessDecision(
      supabase,
      agentID,
      decision.decision_id,
      'verified'
    )

    const { data: request, error: requestError } = await supabase
      .from('verification_requests')
      .update({ status: 'verified' })
      .eq('request_id', requestID)
      .select()
      .single()

    if (requestError) {
      return res.status(500).json({ error: requestError.message })
    }

    await logAction({
      agentID: agentID,
      requestID: requestID,
      action: ACTIONS.ADMIN_APPROVED,
      outcome: OUTCOMES.VERIFIED,
      performedBy: req.user.id,
      ipAddress: req.clientIP,
      details: {
        accessGranted: true,
      },
    })

    await logAction({
      agentID: agentID,
      requestID: requestID,
      action: ACTIONS.ACCESS_GRANTED,
      outcome: OUTCOMES.SUCCESS,
      performedBy: req.user.id,
      ipAddress: req.clientIP,
      details: {
        source: 'admin_approval',
      },
    })

    return res.json({
      request,
      decision,
      access,
      message: 'Agent approved successfully',
    })
  } catch (err) {
    return res.status(500).json({ error: err.message })
  }
}

export async function rejectAgent(req, res) {
  try {
    const { agentID } = req.params
    const { requestID, reason } = req.body

    if (!requestID) {
      return res.status(400).json({ error: 'requestID is required' })
    }

    const { data: decision, error: decisionError } = await supabase
      .from('kyc_decisions')
      .update({
        final_decision: 'rejected',
        verified_probability: 0.0,
        review_probability: 0.0,
        rejected_probability: 1.0,
        decided_at: new Date().toISOString(),
      })
      .eq('request_id', requestID)
      .select()
      .single()

    if (decisionError || !decision) {
      return res.status(404).json({ error: decisionError?.message || 'Decision not found' })
    }

    const access = await enforceAccessDecision(
      supabase,
      agentID,
      decision.decision_id,
      'rejected'
    )

    const { data: request, error: requestError } = await supabase
      .from('verification_requests')
      .update({ status: 'rejected' })
      .eq('request_id', requestID)
      .select()
      .single()

    if (requestError) {
      return res.status(500).json({ error: requestError.message })
    }

    await logAction({
      agentID: agentID,
      requestID: requestID,
      action: ACTIONS.ADMIN_REJECTED,
      outcome: OUTCOMES.REJECTED,
      performedBy: req.user.id,
      ipAddress: req.clientIP,
      details: {
        reason: reason || null,
        accessGranted: false,
      },
    })

    await logAction({
      agentID: agentID,
      requestID: requestID,
      action: ACTIONS.ACCESS_DENIED,
      outcome: OUTCOMES.REJECTED,
      performedBy: req.user.id,
      ipAddress: req.clientIP,
      details: {
        source: 'admin_rejection',
        reason: reason || null,
      },
    })

    return res.json({
      request,
      decision,
      access,
      message: 'Agent rejected successfully',
    })
  } catch (err) {
    return res.status(500).json({ error: err.message })
  }
}

export async function getAllAgents(req, res) {
  try {
    const statusFilter = req.query.status || null

    const { data: agents, error } = await supabase
      .from('agents')
      .select('*')
      .order('created_at', { ascending: false })

    if (error) return res.status(500).json({ error: error.message })

    const results = []
    for (const agent of agents || []) {
      const { data: latestRequest } = await supabase
        .from('verification_requests')
        .select('*')
        .eq('agent_id', agent.agent_id)
        .order('created_at', { ascending: false })
        .limit(1)
        .maybeSingle()

      let scores = null
      let decision = null
      let status = 'pending'

      if (latestRequest) {
        status = latestRequest.status
        const [{ data: scoreRow }, { data: decisionRow }] = await Promise.all([
          supabase
            .from('verification_scores')
            .select('*')
            .eq('request_id', latestRequest.request_id)
            .maybeSingle(),
          supabase
            .from('kyc_decisions')
            .select('*')
            .eq('request_id', latestRequest.request_id)
            .maybeSingle(),
        ])
        scores = scoreRow
        decision = decisionRow
      }

      if (statusFilter && status !== statusFilter) continue

      results.push({
        agent,
        status,
        request: latestRequest,
        scores,
        decision,
      })
    }

    return res.json({ agents: results })
  } catch (err) {
    return res.status(500).json({ error: err.message })
  }
}

export async function getAuditLogs(req, res) {
  try {
    const page = Math.max(1, Number(req.query.page) || 1)
    const pageSize = Math.min(100, Math.max(1, Number(req.query.pageSize) || 20))
    const from = (page - 1) * pageSize
    const to = from + pageSize - 1

    const { data, error, count } = await supabase
      .from('audit_logs')
      .select('*, agents(full_name)', { count: 'exact' })
      .order('timestamp', { ascending: false })
      .range(from, to)

    if (error) return res.status(500).json({ error: error.message })

    const logs = (data || []).map((row) => ({
      logId: row.log_id,
      timestamp: row.timestamp,
      agentId: row.agent_id,
      agentName: row.agents?.full_name || 'Unknown',
      action: row.action,
      outcome: row.outcome,
      requestId: row.request_id,
      details: row.details,
      performedBy: row.performed_by,
      ipAddress: row.ip_address,
    }))

    return res.json({
      logs,
      page,
      pageSize,
      total: count || 0,
    })
  } catch (err) {
    return res.status(500).json({ error: err.message })
  }
}

export async function getAuditLogsByAgent(req, res) {
  try {
    const { agentID } = req.params

    const { data, error } = await supabase
      .from('audit_logs')
      .select('*')
      .eq('agent_id', agentID)
      .order('timestamp', { ascending: false })

    if (error) return res.status(500).json({ error: error.message })

    if (!data || data.length === 0) {
      return res.status(404).json({ error: 'No audit logs found for this agent' })
    }

    const logs = []
    for (const row of data) {
      const performedByLabel = await resolvePerformerLabel(row.performed_by)
      logs.push({
        logId: row.log_id,
        timestamp: row.timestamp,
        agentId: row.agent_id,
        action: row.action,
        outcome: row.outcome,
        requestId: row.request_id,
        details: row.details,
        performedBy: row.performed_by,
        performedByLabel,
        ipAddress: row.ip_address,
      })
    }

    return res.json({ logs })
  } catch (err) {
    return res.status(500).json({ error: err.message })
  }
}

const BUCKET = 'agent-documents'

function storagePathFromFileUrl(fileUrl) {
  if (!fileUrl) return null
  if (!fileUrl.startsWith('http')) return fileUrl

  const markers = [
    `/object/public/${BUCKET}/`,
    `/object/sign/${BUCKET}/`,
    `/object/authenticated/${BUCKET}/`,
  ]

  for (const marker of markers) {
    const index = fileUrl.indexOf(marker)
    if (index !== -1) {
      return decodeURIComponent(fileUrl.slice(index + marker.length).split('?')[0])
    }
  }

  const parts = fileUrl.split(`${BUCKET}/`)
  if (parts.length > 1) {
    return decodeURIComponent(parts[1].split('?')[0])
  }

  return fileUrl
}

function startOfTodayIso() {
  const now = new Date()
  now.setHours(0, 0, 0, 0)
  return now.toISOString()
}

export async function getAgentDocumentImages(req, res) {
  try {
    const { agentID } = req.params

    const { data: documents, error } = await supabase
      .from('documents')
      .select('*')
      .eq('agent_id', agentID)
      .in('document_type', ['national_id', 'id_front', 'id_back', 'passport', 'selfie'])
      .order('uploaded_at', { ascending: false })

    if (error) return res.status(500).json({ error: error.message })

    const primaryDoc =
      documents?.find((doc) => doc.document_type === 'id_front')
      || documents?.find((doc) => doc.document_type === 'passport')
      || documents?.find((doc) => doc.document_type === 'national_id')
    const backDoc = documents?.find((doc) => doc.document_type === 'id_back')
    const selfieDoc = documents?.find((doc) => doc.document_type === 'selfie')

    async function signDocument(doc) {
      if (!doc) return null
      const path = storagePathFromFileUrl(doc.file_url)
      const { data, error: signError } = await supabase.storage
        .from(BUCKET)
        .createSignedUrl(path, 3600)

      if (signError) {
        return {
          documentType: doc.document_type,
          uploadedAt: doc.uploaded_at,
          signedUrl: null,
          error: signError.message,
        }
      }

      return {
        documentType: doc.document_type,
        uploadedAt: doc.uploaded_at,
        signedUrl: data.signedUrl,
      }
    }

    const [documentImage, documentBackImage, selfieImage] = await Promise.all([
      signDocument(primaryDoc),
      signDocument(backDoc),
      signDocument(selfieDoc),
    ])

    return res.json({
      documentImage,
      documentBackImage,
      selfieImage,
    })
  } catch (err) {
    return res.status(500).json({ error: err.message })
  }
}

export async function getDashboardStats(req, res) {
  try {
    const today = startOfTodayIso()

    const [
      totalAgentsRes,
      pendingRes,
      reviewRes,
      verifiedRes,
      rejectedRes,
      todaySubmissionsRes,
      verifiedTodayRes,
      rejectedTodayRes,
    ] = await Promise.all([
      supabase.from('agents').select('agent_id', { count: 'exact', head: true }),
      supabase.from('verification_requests').select('request_id', { count: 'exact', head: true }).eq('status', 'pending'),
      supabase.from('verification_requests').select('request_id', { count: 'exact', head: true }).eq('status', 'review'),
      supabase.from('verification_requests').select('request_id', { count: 'exact', head: true }).eq('status', 'verified'),
      supabase.from('verification_requests').select('request_id', { count: 'exact', head: true }).eq('status', 'rejected'),
      supabase.from('verification_requests').select('request_id', { count: 'exact', head: true }).gte('created_at', today),
      supabase.from('verification_requests').select('request_id', { count: 'exact', head: true }).eq('status', 'verified').gte('created_at', today),
      supabase.from('verification_requests').select('request_id', { count: 'exact', head: true }).eq('status', 'rejected').gte('created_at', today),
    ])

    return res.json({
      totalAgents: totalAgentsRes.count || 0,
      pendingVerification: pendingRes.count || 0,
      awaitingReview: reviewRes.count || 0,
      verified: verifiedRes.count || 0,
      rejected: rejectedRes.count || 0,
      todaySubmissions: todaySubmissionsRes.count || 0,
      verifiedToday: verifiedTodayRes.count || 0,
      rejectedToday: rejectedTodayRes.count || 0,
    })
  } catch (err) {
    return res.status(500).json({ error: err.message })
  }
}

export async function exportAuditLogs(req, res) {
  try {
    const { startDate, endDate, agentID, action, agentName } = req.query

    let agentIdsFilter = null
    if (agentName) {
      const { data: matchedAgents } = await supabase
        .from('agents')
        .select('agent_id, full_name')
        .ilike('full_name', `%${agentName}%`)

      agentIdsFilter = (matchedAgents || []).map((a) => a.agent_id)
      if (agentIdsFilter.length === 0) {
        res.setHeader('Content-Type', 'text/csv')
        res.setHeader('Content-Disposition', 'attachment; filename="audit-logs.csv"')
        return res.send('Timestamp,AgentID,AgentName,Action,Outcome\n')
      }
    }

    let query = supabase
      .from('audit_logs')
      .select('timestamp, agent_id, action, outcome, agents(full_name)')
      .order('timestamp', { ascending: false })
      .limit(10000)

    if (startDate) query = query.gte('timestamp', new Date(startDate).toISOString())
    if (endDate) {
      const end = new Date(endDate)
      end.setHours(23, 59, 59, 999)
      query = query.lte('timestamp', end.toISOString())
    }
    if (agentID) query = query.eq('agent_id', agentID)
    if (agentIdsFilter) query = query.in('agent_id', agentIdsFilter)
    if (action) query = query.eq('action', action)

    const { data, error } = await query
    if (error) return res.status(500).json({ error: error.message })

    const escapeCsv = (value) => {
      const text = String(value ?? '')
      if (text.includes(',') || text.includes('"') || text.includes('\n')) {
        return `"${text.replace(/"/g, '""')}"`
      }
      return text
    }

    const rows = [
      'Timestamp,AgentID,AgentName,Action,Outcome',
      ...(data || []).map((row) => [
        escapeCsv(row.timestamp),
        escapeCsv(row.agent_id),
        escapeCsv(row.agents?.full_name || 'Unknown'),
        escapeCsv(row.action),
        escapeCsv(row.outcome),
      ].join(',')),
    ]

    res.setHeader('Content-Type', 'text/csv')
    res.setHeader('Content-Disposition', 'attachment; filename="audit-logs.csv"')
    return res.send(rows.join('\n'))
  } catch (err) {
    return res.status(500).json({ error: err.message })
  }
}

export async function getRecentActivity(req, res) {
  try {
    const { data, error } = await supabase
      .from('audit_logs')
      .select('log_id, timestamp, agent_id, action, outcome, request_id, agents(full_name)')
      .order('timestamp', { ascending: false })
      .limit(20)

    if (error) return res.status(500).json({ error: error.message })

    const activity = (data || []).map((row) => ({
      logId: row.log_id,
      timestamp: row.timestamp,
      agentId: row.agent_id,
      agentName: row.agents?.full_name || 'Unknown',
      action: row.action,
      outcome: row.outcome,
      requestId: row.request_id,
    }))

    return res.json({ activity })
  } catch (err) {
    return res.status(500).json({ error: err.message })
  }
}

export async function getFlaggedRegistrations(req, res) {
  try {
    const since = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()

    const { data, error } = await supabase
      .from('audit_logs')
      .select('*')
      .eq('action', ACTIONS.FRAUD_GUARDRAIL_TRIGGERED)
      .gte('timestamp', since)
      .order('timestamp', { ascending: false })

    if (error) return res.status(500).json({ error: error.message })

    const entries = (data || []).map((row) => ({
      logId: row.log_id,
      timestamp: row.timestamp,
      agentId: row.agent_id,
      ipAddress: row.ip_address || row.details?.ipAddress || null,
      deviceFingerprint:
        row.device_fingerprint || row.details?.deviceFingerprint || null,
      guardrailType: row.details?.guardrailType || row.details?.guardrail || 'unknown',
      attemptCount: row.details?.attemptCount ?? row.details?.failureCount ?? null,
      outcome: row.outcome,
      details: row.details,
    }))

    const byIp = {}
    for (const entry of entries) {
      const key = entry.ipAddress || 'unknown'
      if (!byIp[key]) {
        byIp[key] = { ipAddress: key, count: 0, entries: [] }
      }
      byIp[key].count += 1
      byIp[key].entries.push(entry)
    }

    const groupedByIp = Object.values(byIp).sort((a, b) => b.count - a.count)

    return res.json({
      entries,
      groupedByIp,
      total: entries.length,
    })
  } catch (err) {
    return res.status(500).json({ error: err.message })
  }
}

export async function resetAgentStrikes(req, res) {
  try {
    const { agentID } = req.params

    const { data: agent, error } = await supabase
      .from('agents')
      .select('agent_id')
      .eq('agent_id', agentID)
      .maybeSingle()

    if (error) return res.status(500).json({ error: error.message })
    if (!agent) return res.status(404).json({ error: 'Agent not found' })

    const before = await getStrikeCount(agentID)
    const result = await resetStrikes(agentID, req.user.id)

    return res.json({
      message: 'Strike count reset successfully',
      previousStrikeCount: result.previousCount ?? before,
      agentId: agentID,
    })
  } catch (err) {
    return res.status(500).json({ error: err.message })
  }
}
