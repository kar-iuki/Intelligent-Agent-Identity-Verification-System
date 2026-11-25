import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { PGlite } from '@electric-sql/pglite'
import { auditWindow } from '../src/utils/auditWindow.js'
import { automatedDecision } from '../src/utils/decisionEvidence.js'

test('admin reviews preserve predictions, record access and restore documented legacy results', async () => {
  const db = new PGlite()
  const one = async (sql, args) => (await db.query(sql, args)).rows[0]
  try {
    await db.exec('create role anon; create role authenticated; create role service_role')
    await db.exec(await readFile(new URL('../../database/schema.sql', import.meta.url), 'utf8'))
    const migration = await readFile(new URL('../../database/manual_review.sql', import.meta.url), 'utf8')
    const user = await one("insert into users(email) values ('review@example.invalid') returning user_id")
    const agent = await one("insert into agents(user_id,full_name,national_id) values ($1,'Test','fixture') returning agent_id", [user.user_id])
    const doc = await one("insert into documents(agent_id,document_type,file_url) values ($1,'passport','') returning document_id", [agent.agent_id])
    async function fixture() {
      const req = await one("insert into verification_requests(agent_id,document_id,status) values ($1,$2,'review') returning request_id", [agent.agent_id, doc.document_id])
      return one(`insert into kyc_decisions(request_id,final_decision,decision_basis,verified_probability,review_probability,rejected_probability)
        values ($1,'review','svm_model',0.23,0.71,0.06) returning *`, [req.request_id])
    }
    for (const recoverable of [true, false]) {
      const d = await fixture()
      if (recoverable) {
        await db.query(`insert into audit_logs(agent_id,request_id,action,outcome,performed_by,details)
          values ($1,$2,'KYC_DECISION_MADE','REVIEW','system',$3)`, [agent.agent_id, d.request_id, JSON.stringify({
          decisionId: d.decision_id, decision: 'review', decisionBasis: 'svm_model',
          verifiedProbability: .23, reviewProbability: .71, rejectedProbability: .06,
        })])
      }
      await db.query("update verification_requests set status='verified' where request_id=$1", [d.request_id])
      await db.query("update kyc_decisions set final_decision='verified', verified_probability=1,review_probability=0,rejected_probability=0 where request_id=$1", [d.request_id])
      await db.query("insert into audit_logs(agent_id,request_id,action,outcome) values ($1,$2,'ADMIN_APPROVED','VERIFIED')", [agent.agent_id,d.request_id])
      await db.exec(migration)
      const previous = automatedDecision(await one('select * from kyc_decisions where request_id=$1',[d.request_id]))
      assert.equal(previous.verified_probability, recoverable ? .23 : null)
      assert.equal(previous.final_decision, recoverable ? 'review' : null)
    }

    for (const status of ['verified', 'rejected']) {
      const original = await fixture()
      const resolve = async (outcome, id = agent.agent_id) => (await one(
        'select resolve_manual_review($1,$2,$3,$4,null,null) as result',
        [id, original.request_id, user.user_id, outcome])).result
      assert.equal((await resolve(status, user.user_id)).status, 404)
      assert.equal((await resolve(status)).status, 409)
      await db.query('insert into access_control_records(agent_id,decision_id) values ($1,$2)', [agent.agent_id, original.decision_id])
      const result = await resolve(status)
      assert.equal(result.request.status, status)
      assert.ok(result.request.admin_reviewed_at)
      assert.equal(result.access.access_granted, status === 'verified')
      assert.deepEqual(await one('select * from kyc_decisions where request_id=$1', [original.request_id]), original)
      const retry = await resolve(status)
      assert.equal(retry.request.admin_reviewed_at, result.request.admin_reviewed_at)
      assert.equal((await resolve(status === 'verified' ? 'rejected' : 'verified')).status, 409)
      assert.equal((await one('select count(*)::int as n from audit_logs where request_id=$1',[original.request_id])).n, 2)
    }
    assert.equal(auditWindow('verified', {final_decision:'review'}, new Date('2026-11-24'),
      '2026-11-01', '2026-11-23T10:00:00Z').expiresAt, '2026-11-26T10:00:00.000Z')
  } finally { await db.close() }
})
