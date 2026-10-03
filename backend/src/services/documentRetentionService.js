import { auditWindow } from '../utils/auditWindow.js'

const BUCKET = 'agent-documents'
const DOCUMENT_TYPES = ['national_id', 'id_front', 'id_back', 'passport', 'drivers_licence', 'selfie']

function storagePath(value, agentId) {
  if (!value) return null
  let path = value
  if (/^https?:/.test(path)) {
    const match = new URL(path).pathname.match(/\/object\/(?:public|sign|authenticated)\/agent-documents\/(.+)/)
    if (!match) return null
    path = decodeURIComponent(match[1])
  }
  return path.startsWith(`${agentId}/`) && !path.split('/').includes('..') ? path : null
}

// Keep document rows, decisions, scores, and audit history intact. Deleting a
// document row would cascade into verification history in the existing schema.
export async function purgeExpiredDocuments(client, now = new Date()) {
  let removed = 0
  const failures = []
  for (let offset = 0; ; offset += 100) {
    const { data: agents, error } = await client.from('agents').select('agent_id')
      .order('agent_id').range(offset, offset + 99)
    if (error) throw error
    for (const agent of agents || []) {
      try {
        const { data: request, error: requestError } = await client.from('verification_requests')
          .select('request_id, status').eq('agent_id', agent.agent_id)
          .order('created_at', { ascending: false }).limit(1).maybeSingle()
        if (requestError) throw requestError
        if (request?.status !== 'verified') continue
        const { data: decision, error: decisionError } = await client.from('kyc_decisions')
          .select('final_decision, decided_at').eq('request_id', request.request_id).maybeSingle()
        if (decisionError) throw decisionError
        const window = auditWindow(request.status, decision, now)
        if (!window.expiresAt || new Date(window.expiresAt) > now) continue

        const { data: documents, error: documentsError } = await client.from('documents')
          .select('document_id, file_url, uploaded_at').eq('agent_id', agent.agent_id)
          .in('document_type', DOCUMENT_TYPES).lte('uploaded_at', window.verifiedAt).neq('file_url', '')
        if (documentsError) throw documentsError
        // Include superseded uploads, which no longer have a documents row.
        // New uploads use unique names so cleanup cannot delete a replacement.
        const paths = new Set()
        for (const folder of ['documents', 'selfies']) {
          for (let page = 0; ; page += 100) {
            const prefix = `${agent.agent_id}/${folder}`
            const { data: files, error: listError } = await client.storage.from(BUCKET)
              .list(prefix, { limit: 100, offset: page, sortBy: { column: 'name', order: 'asc' } })
            if (listError) throw listError
            for (const file of files || []) {
              const modifiedAt = file.updated_at || file.created_at
              if (file.id && modifiedAt && new Date(modifiedAt) <= new Date(window.verifiedAt)) {
                paths.add(`${prefix}/${file.name}`)
              }
            }
            if (!files || files.length < 100) break
          }
        }
        for (const document of documents || []) {
          const path = storagePath(document.file_url, agent.agent_id)
          if (path) paths.add(path)
        }
        if (paths.size) {
          const { error: removeError } = await client.storage.from(BUCKET).remove([...paths])
          if (removeError) throw removeError
        }
        for (const document of documents || []) {
          const path = storagePath(document.file_url, agent.agent_id)
          if (!path) continue
          const { error: updateError } = await client.from('documents').update({ file_url: '' })
            .eq('document_id', document.document_id).eq('file_url', document.file_url)
            .eq('uploaded_at', document.uploaded_at)
          if (updateError) throw updateError
          removed++
        }
      } catch (error) {
        failures.push(error)
      }
    }
    if (!agents || agents.length < 100) break
  }
  if (failures.length) throw new AggregateError(failures, failures.map(error => error.message).join('; '))
  return removed
}

export function startDocumentRetention(client) {
  let running = false
  const run = async () => {
    if (running) return
    running = true
    try {
      await purgeExpiredDocuments(client)
    } catch (error) {
      console.error('Document retention cleanup failed:', error.message)
    } finally { running = false }
  }
  void run()
  const timer = setInterval(run, 15 * 60 * 1000)
  timer.unref()
  return timer
}
