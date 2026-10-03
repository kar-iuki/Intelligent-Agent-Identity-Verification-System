import test from 'node:test'
import assert from 'node:assert/strict'
import { auditExpiresAt, auditWindow } from '../src/utils/auditWindow.js'
import { purgeExpiredDocuments } from '../src/services/documentRetentionService.js'

test('three full Nairobi business days skip weekends and cross months', () => {
  assert.equal(auditExpiresAt('2026-10-02T10:00:00Z'), '2026-10-07T10:00:00.000Z')
  assert.equal(auditExpiresAt('2026-10-03T10:00:00Z'), '2026-10-07T10:00:00.000Z')
  assert.equal(auditExpiresAt('2026-10-05T10:00:00Z'), '2026-10-08T10:00:00.000Z')
  assert.equal(auditExpiresAt('2026-12-31T22:00:00Z'), '2027-01-05T22:00:00.000Z')
  assert.equal(auditExpiresAt(null), null)
  assert.equal(auditExpiresAt('invalid'), null)
})

test('window uses successful decision time and closes exactly at expiry', () => {
  const decision = { final_decision: 'verified', decided_at: '2026-10-02T10:00:00Z' }
  assert.equal(auditWindow('verified', decision, new Date('2026-10-07T09:59:59Z')).open, true)
  assert.equal(auditWindow('verified', decision, new Date('2026-10-07T10:00:00Z')).open, false)
  assert.equal(auditWindow('review', decision).expiresAt, null)
  assert.equal(auditWindow('verified', null).open, false)
})

function fixture({ status = 'verified', storageFailure = false } = {}) {
  const removed = [], updates = []
  const verifiedAt = '2026-10-02T10:00:00Z'
  const rows = {
    agents: [{ agent_id: 'agent-1' }],
    verification_requests: { request_id: 'request-1', status },
    kyc_decisions: { final_decision: 'verified', decided_at: verifiedAt },
    documents: [{ document_id: 'doc-1', file_url: 'agent-1/documents/front.jpg', uploaded_at: verifiedAt }],
  }
  const client = {
    from(table) {
      let update = false
      const query = {
        select() { return this }, order() { return this }, range() { return this },
        limit() { return this }, maybeSingle() { return this }, in() { return this },
        eq() { return this }, neq() { return this },
        lte(column, value) { assert.equal(column, 'uploaded_at'); assert.equal(value, verifiedAt); return this },
        update(value) { assert.equal(table, 'documents'); updates.push(value); update = true; return this },
        then(resolve) { return Promise.resolve({ data: update ? null : rows[table], error: null }).then(resolve) },
      }
      return query
    },
    storage: { from() { return {
      async list(prefix) { return { data: prefix.endsWith('documents') ? [
        { id: 'old', name: 'older.jpg', updated_at: verifiedAt },
        { id: 'new', name: 'replacement.jpg', updated_at: '2026-10-08T09:00:00Z' },
      ] : [] } },
      async remove(paths) { removed.push(...paths); return { error: storageFailure ? new Error('Storage unavailable') : null } },
    } } },
  }
  return { client, removed, updates }
}

test('purges expired and superseded images while preserving metadata and newer uploads', async () => {
  const f = fixture()
  assert.equal(await purgeExpiredDocuments(f.client, new Date('2026-10-08T10:00:00Z')), 1)
  assert.deepEqual(f.removed.sort(), ['agent-1/documents/front.jpg', 'agent-1/documents/older.jpg'])
  assert.deepEqual(f.updates, [{ file_url: '' }])
})

test('does not delete files inside the window or for pending/review/rejected requests', async () => {
  for (const status of ['pending', 'review', 'rejected', 'verified']) {
    const f = fixture({ status })
    await purgeExpiredDocuments(f.client, new Date(status === 'verified' ? '2026-10-05T10:00:00Z' : '2026-10-08T10:00:00Z'))
    assert.deepEqual(f.removed, [])
    assert.deepEqual(f.updates, [])
  }
})

test('failed storage deletion preserves file references for retry', async () => {
  const f = fixture({ storageFailure: true })
  await assert.rejects(purgeExpiredDocuments(f.client, new Date('2026-10-08T10:00:00Z')), /Storage unavailable/)
  assert.deepEqual(f.updates, [])
})
