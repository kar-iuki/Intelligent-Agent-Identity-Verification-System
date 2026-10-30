import test from 'node:test'
import assert from 'node:assert/strict'
import { requiresDocumentCamera, documentCaptureError } from '../src/services/documentCapturePolicy.js'

test('camera requirement comes from saved attempts and fails closed on storage failure', async () => {
  const calls = []
  const db = result => ({ from: table => {
    calls.push(table)
    return { select: () => ({ eq: (column, id) => {
      assert.equal(column, 'agent_id'); assert.equal(id, 'agent-1')
      return { limit: async () => result }
    } }) }
  } })
  assert.equal(await requiresDocumentCamera(db({ data:[] }), 'agent-1'), false)
  assert.equal(await requiresDocumentCamera(db({ data:[{ request_id:'first' }] }), 'agent-1'), true)
  await assert.rejects(requiresDocumentCamera(db({ error:new Error('offline') }), 'agent-1'))
  assert.deepEqual(calls, Array(3).fill('verification_requests'))
})

test('retries reject uploaded, missing-source and legacy document images but permit camera photos and selfie-only replacement', () => {
  const documentFront = {}, documentBack = {}
  assert.equal(documentCaptureError(false, { documentFront }), null)
  assert.ok(documentCaptureError(true, { documentFront }))
  assert.ok(documentCaptureError(true, { documentFront }, { documentFrontSource:'upload' }))
  assert.ok(documentCaptureError(true, { documentBack }, { documentBackSource:'upload' }))
  assert.ok(documentCaptureError(true, { documentFront, documentBack }, { documentFrontSource:'camera' }))
  assert.ok(documentCaptureError(true, { legacyDocument:{} }, { documentFrontSource:'camera' }))
  assert.equal(documentCaptureError(true, { documentFront, documentBack }, { documentFrontSource:'camera', documentBackSource:'camera' }), null)
  assert.equal(documentCaptureError(true, {}), null)
})

test('upload controller rejects retry uploads before writing document storage', async () => {
  process.env.SUPABASE_URL = 'http://localhost:54321'
  process.env.SUPABASE_SERVICE_ROLE_KEY = 'test-only'
  const { default: db } = await import('../src/utils/supabaseClient.js')
  const { uploadDocuments, getRegistrationStatus } = await import('../src/controllers/agentController.js')
  const originalFrom = db.from
  const agent = { agent_id:'agent-1', full_name:'Test Agent', phone_number:'1234567', national_id:'123', date_of_birth:'1990-01-01' }
  db.from = table => {
    const result = table === 'agents' ? { data:agent } : table === 'verification_requests' ? { data:[{ request_id:'first' }] } : { data:[] }
    const query = { select:() => query, eq:() => query, limit:async () => result, single:async () => result, then:resolve => resolve(result) }
    return query
  }
  const response = () => ({ statusCode:200, status(code) { this.statusCode = code; return this }, json(body) { this.body = body; return this } })
  try {
    for (const documentKind of ['national_id', 'passport', 'drivers_licence']) {
      for (const source of [undefined, 'upload']) {
        const res = response()
        await uploadDocuments({ user:{ id:'user-1' }, body:{ documentKind, documentFrontSource:source }, files:{ documentFront:[{}] } }, res)
        assert.equal(res.statusCode, 400)
        assert.equal(res.body.code, 'DOCUMENT_CAMERA_REQUIRED')
      }
    }
    const res = response()
    await getRegistrationStatus({ user:{ id:'user-1' } }, res)
    assert.equal(res.body.documentCameraRequired, true)
  } finally { db.from = originalFrom }
})
