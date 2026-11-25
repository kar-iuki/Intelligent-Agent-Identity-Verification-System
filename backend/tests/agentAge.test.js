import test from 'node:test'
import assert from 'node:assert/strict'
import { validateDateOfBirth as apiCheck } from '../src/utils/validateDateOfBirth.js'
import { latestEligibleBirthDate, validateDateOfBirth as formCheck } from '../../frontend/src/utils/agentAge.js'

for (const [description, instant, cutoff, nextDay] of [
  ['before midnight in Nairobi', '2026-11-24T20:59:59Z', '2008-11-24', '2008-11-25'],
  ['on the eighteenth birthday', '2026-11-24T21:00:00Z', '2008-11-25', '2008-11-26'],
  ['on a leap day', '2024-02-29T12:00:00Z', '2006-02-28', '2006-03-01'],
  ['before a leap-day birthday in a non-leap year', '2026-02-28T12:00:00Z', '2008-02-28', '2008-02-29'],
  ['after a leap-day birthday in a non-leap year', '2026-03-01T12:00:00Z', '2008-03-01', '2008-03-02'],
]) {
  test(description, () => {
    const now = new Date(instant)
    assert.equal(latestEligibleBirthDate(now), cutoff)
    for (const check of [formCheck, apiCheck]) {
      assert.equal(check(cutoff, now), null)
      assert.match(check(nextDay, now), /at least 18/)
    }
  })
}

test('both checks reject missing, impossible and future dates', () => {
  for (const dob of ['', null, '2005-02-29', '2001-04-31', '2030-01-01']) {
    for (const check of [formCheck, apiCheck]) {
      assert.ok(check(dob, new Date('2026-11-25T12:00:00Z')))
    }
  }
})
