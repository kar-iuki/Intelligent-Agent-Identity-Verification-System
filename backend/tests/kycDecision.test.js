import test from 'node:test'
import assert from 'node:assert/strict'
process.env.SUPABASE_URL = 'https://example.supabase.co'
process.env.SUPABASE_SERVICE_ROLE_KEY = 'local-test-placeholder'
const { makeKYCDecision } = await import('../src/services/accessControlService.js')
const scores = { faceMatchScore: 84.5, livenessScore: .93, ocrConfidenceScore: .88,
  blurScore: 72, brightnessScore: 181, contrastScore: 46 }

test('Incomplete scores fail before inference or threshold fallback', async () => {
  const original = globalThis.fetch
  globalThis.fetch = () => { throw new Error('Network must not be called') }
  try {
    for (const name of Object.keys(scores)) {
      for (const bad of [undefined, null, true, '0.8', NaN, Infinity, -1]) {
        await assert.rejects(makeKYCDecision({ ...scores, [name]: bad }), /Missing or invalid verification score/)
      }
    }
  } finally { globalThis.fetch = original }
})

test('Model prediction preserves database enums and decision basis', async () => {
  const original = globalThis.fetch
  const calls = []
  globalThis.fetch = async (url, options) => {
    calls.push(String(url))
    if (String(url).endsWith('/status')) {
      return new Response(JSON.stringify({ model_loaded: true, model_version: '2.0.0' }), { status: 200 })
    }
    assert.deepEqual(JSON.parse(options.body), scores)
    return new Response(JSON.stringify({ finalDecision: 'review', verifiedProbability: .2,
      reviewProbability: .7, rejectedProbability: .1, decisionBasis: 'svm_model', modelVersion: '2.0.0' }), { status: 200 })
  }
  try {
    const result = await makeKYCDecision(scores)
    assert.equal(result.finalDecision, 'review')
    assert.equal(result.decisionBasis, 'svm_model')
    assert.equal(result.modelVersion, '2.0.0')
    assert.equal(calls.length, 2)
  } finally { globalThis.fetch = original }
})
