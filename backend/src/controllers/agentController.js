import supabase from '../utils/supabaseClient.js'

const BUCKET = 'agent-documents'
const ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png']
const MAX_FILE_SIZE = 5 * 1024 * 1024

async function getAgentForUser(userId) {
  const { data, error } = await supabase
    .from('agents')
    .select('*')
    .eq('user_id', userId)
    .single()

  if (error || !data) {
    return null
  }

  return data
}

async function writeAuditLog(agentId, action, outcome, requestId = null) {
  const { error } = await supabase.from('audit_logs').insert({
    agent_id: agentId,
    request_id: requestId,
    action,
    outcome,
  })

  if (error) {
    console.error('Failed to write audit log:', error.message)
  }
}

async function ensureBucket() {
  const { data: buckets } = await supabase.storage.listBuckets()
  const exists = buckets?.some((bucket) => bucket.name === BUCKET)

  if (!exists) {
    const { error } = await supabase.storage.createBucket(BUCKET, {
      public: false,
      fileSizeLimit: MAX_FILE_SIZE,
      allowedMimeTypes: ALLOWED_MIME_TYPES,
    })

    if (error && !error.message?.toLowerCase().includes('already')) {
      throw new Error(`Failed to create storage bucket: ${error.message}`)
    }
  }
}

function extensionForMime(mimeType) {
  return mimeType === 'image/png' ? 'png' : 'jpg'
}

function hasPersonalDetails(agent) {
  return Boolean(
    agent?.full_name?.trim()
    && agent?.phone_number?.trim()
    && agent?.national_id?.trim()
  )
}

export async function submitRegistration(req, res) {
  const { fullName, phoneNumber, nationalID } = req.body

  if (!fullName || !phoneNumber || !nationalID) {
    return res.status(400).json({ error: 'Full name, phone number, and national ID are required' })
  }

  const agent = await getAgentForUser(req.user.id)
  if (!agent) {
    return res.status(404).json({ error: 'Agent profile not found' })
  }

  const { data: existingNationalId } = await supabase
    .from('agents')
    .select('agent_id')
    .eq('national_id', nationalID)
    .neq('agent_id', agent.agent_id)
    .maybeSingle()

  if (existingNationalId) {
    return res.status(409).json({
      error: 'An agent with this national ID is already registered.',
    })
  }

  const { data: updatedAgent, error } = await supabase
    .from('agents')
    .update({
      full_name: fullName.trim(),
      phone_number: phoneNumber.trim(),
      national_id: nationalID.trim(),
    })
    .eq('agent_id', agent.agent_id)
    .select()
    .single()

  if (error) {
    await writeAuditLog(agent.agent_id, 'submit_registration', 'failed')
    return res.status(400).json({ error: error.message })
  }

  await writeAuditLog(agent.agent_id, 'submit_registration', 'success')

  return res.json({ agent: updatedAgent })
}

export async function uploadDocuments(req, res) {
  try {
    const agent = await getAgentForUser(req.user.id)
    if (!agent) {
      return res.status(404).json({ error: 'Agent profile not found' })
    }

    if (!hasPersonalDetails(agent)) {
      return res.status(400).json({
        error: 'Complete personal details before uploading documents',
      })
    }

    const documentFile = req.files?.documentImage?.[0]
    const selfieFile = req.files?.selfieImage?.[0]

    if (!documentFile || !selfieFile) {
      return res.status(400).json({
        error: 'Both documentImage and selfieImage files are required',
      })
    }

    for (const file of [documentFile, selfieFile]) {
      if (!ALLOWED_MIME_TYPES.includes(file.mimetype)) {
        return res.status(400).json({ error: 'Only JPEG and PNG image files are allowed' })
      }
      if (file.size > MAX_FILE_SIZE) {
        return res.status(400).json({ error: 'Each file must be 5MB or smaller' })
      }
    }

    await ensureBucket()

    const documentExt = extensionForMime(documentFile.mimetype)
    const selfieExt = extensionForMime(selfieFile.mimetype)
    const documentPath = `${agent.agent_id}/documents/documentImage.${documentExt}`
    const selfiePath = `${agent.agent_id}/selfies/selfieImage.${selfieExt}`

    const { error: documentUploadError } = await supabase.storage
      .from(BUCKET)
      .upload(documentPath, documentFile.buffer, {
        contentType: documentFile.mimetype,
        upsert: true,
      })

    if (documentUploadError) {
      await writeAuditLog(agent.agent_id, 'upload_documents', 'failed')
      return res.status(500).json({ error: documentUploadError.message })
    }

    const { error: selfieUploadError } = await supabase.storage
      .from(BUCKET)
      .upload(selfiePath, selfieFile.buffer, {
        contentType: selfieFile.mimetype,
        upsert: true,
      })

    if (selfieUploadError) {
      await writeAuditLog(agent.agent_id, 'upload_documents', 'failed')
      return res.status(500).json({ error: selfieUploadError.message })
    }

    // Private bucket: store object paths as durable references.
    const documentFileUrl = documentPath
    const selfieFileUrl = selfiePath

    const { data: existingDocs } = await supabase
      .from('documents')
      .select('document_id, document_type')
      .eq('agent_id', agent.agent_id)
      .in('document_type', ['national_id', 'selfie'])

    let documentRecord

    const existingNationalIdDoc = existingDocs?.find((doc) => doc.document_type === 'national_id')
    const existingSelfieDoc = existingDocs?.find((doc) => doc.document_type === 'selfie')

    if (existingNationalIdDoc) {
      const { data, error } = await supabase
        .from('documents')
        .update({ file_url: documentFileUrl, uploaded_at: new Date().toISOString() })
        .eq('document_id', existingNationalIdDoc.document_id)
        .select()
        .single()

      if (error) {
        await writeAuditLog(agent.agent_id, 'upload_documents', 'failed')
        return res.status(500).json({ error: error.message })
      }
      documentRecord = data
    } else {
      const { data, error } = await supabase
        .from('documents')
        .insert({
          agent_id: agent.agent_id,
          document_type: 'national_id',
          file_url: documentFileUrl,
        })
        .select()
        .single()

      if (error) {
        await writeAuditLog(agent.agent_id, 'upload_documents', 'failed')
        return res.status(500).json({ error: error.message })
      }
      documentRecord = data
    }

    if (existingSelfieDoc) {
      const { error } = await supabase
        .from('documents')
        .update({ file_url: selfieFileUrl, uploaded_at: new Date().toISOString() })
        .eq('document_id', existingSelfieDoc.document_id)

      if (error) {
        await writeAuditLog(agent.agent_id, 'upload_documents', 'failed')
        return res.status(500).json({ error: error.message })
      }
    } else {
      const { error } = await supabase
        .from('documents')
        .insert({
          agent_id: agent.agent_id,
          document_type: 'selfie',
          file_url: selfieFileUrl,
        })

      if (error) {
        await writeAuditLog(agent.agent_id, 'upload_documents', 'failed')
        return res.status(500).json({ error: error.message })
      }
    }

    await writeAuditLog(agent.agent_id, 'upload_documents', 'success')

    return res.status(201).json({
      document: documentRecord,
      selfieUrl: selfieFileUrl,
    })
  } catch (err) {
    console.error('uploadDocuments error:', err)
    return res.status(500).json({ error: err.message || 'Document upload failed' })
  }
}

export async function getAgentProfile(req, res) {
  const agent = await getAgentForUser(req.user.id)
  if (!agent) {
    return res.status(404).json({ error: 'Agent profile not found' })
  }

  const { data: documents, error } = await supabase
    .from('documents')
    .select('*')
    .eq('agent_id', agent.agent_id)
    .order('uploaded_at', { ascending: false })

  if (error) {
    return res.status(500).json({ error: error.message })
  }

  const status = await resolveRegistrationStatus(agent, documents || [])

  return res.json({
    agent,
    documents: documents || [],
    email: req.user.email,
    status,
  })
}

export async function getRegistrationStatus(req, res) {
  const agent = await getAgentForUser(req.user.id)
  if (!agent) {
    return res.status(404).json({ error: 'Agent profile not found' })
  }

  const { data: documents, error } = await supabase
    .from('documents')
    .select('document_id, document_type')
    .eq('agent_id', agent.agent_id)

  if (error) {
    return res.status(500).json({ error: error.message })
  }

  const status = await resolveRegistrationStatus(agent, documents || [])

  return res.json({ status })
}

async function resolveRegistrationStatus(agent, documents) {
  if (!hasPersonalDetails(agent)) {
    return 'incomplete'
  }

  const hasNationalIdDoc = documents.some((doc) => doc.document_type === 'national_id')
  const hasSelfieDoc = documents.some((doc) => doc.document_type === 'selfie')

  if (hasNationalIdDoc && hasSelfieDoc) {
    return 'verification_pending'
  }

  // Personal details saved; waiting for document + selfie upload
  return 'documents_submitted'
}
