import { it } from 'vitest'
import assert from 'node:assert/strict'
import { faceYaw, selfieFraming, selfieGuide } from '../../src/utils/selfieFraming.js'

function face(aspect, height, turn = 0, x = 0.5) {
  const width = height * 0.72 / aspect
  const points = Array.from({ length: 478 }, () => ({ x, y: 0.5 }))
  points[234].x -= width / 2
  points[454].x += width / 2
  points[10].y -= height / 2
  points[152].y += height / 2
  points[1].x += turn * width
  return points
}

for (const aspect of [16 / 9, 4 / 3, 9 / 16, 21 / 9]) {
  it(`fits the guide in the frame and accepts a smaller face at aspect ${aspect}`, () => {
    const guide = selfieGuide(aspect)
    assert.ok(guide.width <= 0.85 && guide.height <= 0.8)
    assert.ok(Math.abs(guide.width * aspect / guide.height - 0.76) < 1e-9)
    assert.equal(selfieFraming(face(aspect, 0.28), guide), 'ready')
    assert.equal(selfieFraming(face(aspect, 0.1), guide), 'tooFar')
    assert.equal(selfieFraming(face(aspect, 0.78), guide), 'tooClose')
    assert.equal(selfieFraming(face(aspect, 0.28, 0.22), guide), 'turnForward')
  })
}

it('withholds capture when an outline landmark crosses the oval', () => {
  const guide = selfieGuide(16 / 9)
  const points = face(16 / 9, 0.32)
  points[172] = { x: 0.5 + guide.width * 0.4, y: 0.5 + guide.height * 0.4 }
  assert.equal(selfieFraming(points, guide), 'offCentre')
})

it('measures the same left or right turn at two distances and camera positions', () => {
  for (const turn of [-0.20, 0, 0.20]) {
    for (const height of [0.28, 0.54]) {
      const yaw = faceYaw(face(16 / 9, height, turn, 0.55))
      assert.ok(Math.abs(yaw - turn) < 1e-9)
    }
  }
  assert.ok(Number.isNaN(faceYaw([])))
})
