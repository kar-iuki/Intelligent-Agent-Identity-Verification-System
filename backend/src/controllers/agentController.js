import supabase from '../utils/supabaseClient.js'
import { logAction, ACTIONS, OUTCOMES } from '../utils/auditLogger.js'
import { assessSingleImageQuality } from '../services/verificationService.js'
import { validateDateOfBirth } from '../utils/validateDateOfBirth.js'

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
    && agent?.date_of_birth
  )
}

export async function submitRegistration(req, res) {
  const { fullName, phoneNumber, nationalID, dateOfBirth } = req.body

  if (!fullName || !phoneNumber || !nationalID || !dateOfBirth) {
    return res.status(400).json({
      error: 'Full name, phone number, national ID, and date of birth are required',
    })
  }

  const dobError = validateDateOfBirth(dateOfBirth)
  if (dobError) {
    return res.status(400).json({ error: dobError })
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
      date_of_birth: String(dateOfBirth).trim(),
    })
    .eq('agent_id', agent.agent_id)
    .select()
    .single()

  if (error) {
    await logAction({
      agentID: agent.agent_id,
      action: ACTIONS.AGENT_REGISTERED,
      outcome: OUTCOMES.FAILED,
      performedBy: req.user.id,
      ipAddress: req.clientIP,
      details: { reason: error.message },
    })
    return res.status(400).json({ error: error.message })
  }

  await logAction({
    agentID: agent.agent_id,
    action: ACTIONS.AGENT_REGISTERED,
    outcome: OUTCOMES.SUCCESS,
    performedBy: req.user.id,
    ipAddress: req.clientIP,
    details: { source: 'agent_dashboard_registration' },
  })

  return res.json({ agent: updatedAgent })
}

export async function checkImageQuality(req, res) {
  try {
    const imageFile = req.file
    if (!imageFile) {
      return res.status(400).json({ error: 'image file is required' })
    }

    if (!ALLOWED_MIME_TYPES.includes(imageFile.mimetype)) {
      return res.status(400).json({ error: 'Only JPEG and PNG image files are allowed' })
    }
    if (imageFile.size > MAX_FILE_SIZE) {
      return res.status(400).json({ error: 'Each file must be 5MB or smaller' })
    }

    const purpose = String(req.body?.purpose || 'document').toLowerCase()
    const result = await assessSingleImageQuality(imageFile.buffer, {
      filename: imageFile.originalname || 'image.jpg',
      mime: imageFile.mimetype,
      purpose: purpose === 'selfie' ? 'selfie' : 'document',
    })

    return res.json(result)
  } catch (err) {
    console.error('checkImageQuality error:', err)
    return res.status(500).json({ error: err.message || 'Image quality check failed' })
  }
}

async function upsertDocumentRecord(agentId, documentType, fileUrl) {
  const { data: existing } = await supabase
    .from('documents')
    .select('document_id')
    .eq('agent_id', agentId)
    .eq('document_type', documentType)
    .maybeSingle()

  if (existing?.document_id) {
    const { data, error } = await supabase
      .from('documents')
      .update({ file_url: fileUrl, uploaded_at: new Date().toISOString() })
      .eq('document_id', existing.document_id)
      .select()
      .single()
    if (error) throw new Error(error.message)
    return data
  }

  const { data, error } = await supabase
    .from('documents')
    .insert({
      agent_id: agentId,
      document_type: documentType,
      file_url: fileUrl,
    })
    .select()
    .single()

  if (error) throw new Error(error.message)
  return data
}

async function uploadBufferToStorage(path, file) {
  const { error } = await supabase.storage
    .from(BUCKET)
    .upload(path, file.buffer, {
      contentType: file.mimetype,
      upsert: true,
    })
  if (error) throw new Error(error.message)
  return path
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

    const documentKind = String(req.body?.documentKind || 'national_id').toLowerCase()
    const legacyDocument = req.files?.documentImage?.[0]
    const documentFront = req.files?.documentFront?.[0] || legacyDocument
    const documentBack = req.files?.documentBack?.[0]
    const selfieFile = req.files?.selfieImage?.[0]
    const selfieChallenge = req.body?.selfieChallenge || null

    const updatingDocument = Boolean(documentFront)
    const updatingSelfie = Boolean(selfieFile)

    if (!updatingDocument && !updatingSelfie) {
      return res.status(400).json({
        error: 'Provide at least a document image or a selfie image to upload',
      })
    }

    if (updatingDocument && documentKind === 'national_id' && !documentBack && !legacyDocument) {
      // Allow front-only replace when back already exists (partial recapture of front)
      const { data: existingBack } = await supabase
        .from('documents')
        .select('document_id')
        .eq('agent_id', agent.agent_id)
        .eq('document_type', 'id_back')
        .maybeSingle()

      if (!existingBack) {
        return res.status(400).json({
          error: 'National ID uploads require both front and back images',
        })
      }
    }

    const filesToValidate = []
    if (documentFront) filesToValidate.push(documentFront)
    if (documentBack) filesToValidate.push(documentBack)
    if (selfieFile) filesToValidate.push(selfieFile)

    for (const file of filesToValidate) {
      if (!ALLOWED_MIME_TYPES.includes(file.mimetype)) {
        return res.status(400).json({ error: 'Only JPEG and PNG image files are allowed' })
      }
      if (file.size > MAX_FILE_SIZE) {
        return res.status(400).json({ error: 'Each file must be 5MB or smaller' })
      }
    }

    // Partial replace must keep a complete set on file
    if (!updatingDocument || !updatingSelfie) {
      const { data: existingDocs, error: existingError } = await supabase
        .from('documents')
        .select('document_type')
        .eq('agent_id', agent.agent_id)

      if (existingError) {
        return res.status(500).json({ error: existingError.message })
      }

      const types = new Set((existingDocs || []).map((doc) => doc.document_type))
      const hasIdentity = ['national_id', 'id_front', 'passport'].some((t) => types.has(t))
      const hasSelfie = types.has('selfie')

      if (!updatingDocument && !hasIdentity) {
        return res.status(400).json({
          error: 'Upload an identity document before replacing only the selfie',
        })
      }
      if (!updatingSelfie && !hasSelfie) {
        return res.status(400).json({
          error: 'Upload a selfie before replacing only the identity document',
        })
      }
    }

    await ensureBucket()

    const failUpload = async (reason) => {
      await logAction({
        agentID: agent.agent_id,
        action: ACTIONS.DOCUMENTS_UPLOADED,
        outcome: OUTCOMES.FAILED,
        performedBy: req.user.id,
        ipAddress: req.clientIP,
        details: { reason, documentKind, updatingDocument, updatingSelfie },
      })
    }

    try {
      let primaryDocumentType = null
      let primaryPath = null
      let backPath = null
      let selfiePath = null

      if (updatingDocument) {
        const frontExt = extensionForMime(documentFront.mimetype)

        if (documentKind === 'passport') {
          primaryDocumentType = 'passport'
          primaryPath = `${agent.agent_id}/documents/passport.${frontExt}`
          await uploadBufferToStorage(primaryPath, documentFront)
          await upsertDocumentRecord(agent.agent_id, 'passport', primaryPath)
          await upsertDocumentRecord(agent.agent_id, 'national_id', primaryPath)
        } else {
          primaryDocumentType = 'id_front'
          primaryPath = `${agent.agent_id}/documents/id_front.${frontExt}`
          await uploadBufferToStorage(primaryPath, documentFront)
          await upsertDocumentRecord(agent.agent_id, 'id_front', primaryPath)
          await upsertDocumentRecord(agent.agent_id, 'national_id', primaryPath)

          if (documentBack) {
            const backExt = extensionForMime(documentBack.mimetype)
            backPath = `${agent.agent_id}/documents/id_back.${backExt}`
            await uploadBufferToStorage(backPath, documentBack)
            await upsertDocumentRecord(agent.agent_id, 'id_back', backPath)
          }
        }
      }

      if (updatingSelfie) {
        const selfieExt = extensionForMime(selfieFile.mimetype)
        selfiePath = `${agent.agent_id}/selfies/selfieImage.${selfieExt}`
        await uploadBufferToStorage(selfiePath, selfieFile)
        await upsertDocumentRecord(agent.agent_id, 'selfie', selfiePath)
      }

      await logAction({
        agentID: agent.agent_id,
        action: ACTIONS.DOCUMENTS_UPLOADED,
        outcome: OUTCOMES.SUCCESS,
        performedBy: req.user.id,
        ipAddress: req.clientIP,
        details: {
          documentKind,
          primaryDocumentType,
          primaryPath,
          backPath,
          selfiePath,
          selfieChallenge,
          partial: !(updatingDocument && updatingSelfie),
        },
      })

      return res.status(201).json({
        documentKind,
        documentType: primaryDocumentType,
        documentUrl: primaryPath,
        backUrl: backPath,
        selfieUrl: selfiePath,
        partial: !(updatingDocument && updatingSelfie),
      })
    } catch (uploadErr) {
      await failUpload(uploadErr.message)
      return res.status(500).json({ error: uploadErr.message })
    }
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

export async function getAgentAuditLogs(req, res) {
  try {
    const agent = await getAgentForUser(req.user.id)
    if (!agent) {
      return res.status(404).json({ error: 'Agent profile not found' })
    }

    const { data, error } = await supabase
      .from('audit_logs')
      .select('*')
      .eq('agent_id', agent.agent_id)
      .order('timestamp', { ascending: false })

    if (error) {
      return res.status(500).json({ error: error.message })
    }

    return res.json({
      logs: (data || []).map((row) => ({
        logId: row.log_id,
        timestamp: row.timestamp,
        action: row.action,
        outcome: row.outcome,
        details: row.details,
        performedBy: row.performed_by,
        requestId: row.request_id,
        ipAddress: row.ip_address,
      })),
    })
  } catch (err) {
    return res.status(500).json({ error: err.message })
  }
}

async function resolveRegistrationStatus(agent, documents) {
  if (!hasPersonalDetails(agent)) {
    return 'incomplete'
  }

  const identityTypes = new Set(['national_id', 'id_front', 'passport'])
  const hasIdentityDoc = documents.some((doc) => identityTypes.has(doc.document_type))
  const hasSelfieDoc = documents.some((doc) => doc.document_type === 'selfie')

  if (hasIdentityDoc && hasSelfieDoc) {
    return 'verification_pending'
  }

  return 'documents_submitted'
}
