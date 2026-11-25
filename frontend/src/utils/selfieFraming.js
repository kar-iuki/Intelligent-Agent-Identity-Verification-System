// All positions are fractions of the uncropped video frame.
export function selfieGuide(aspect) {
  const height = Math.min(0.8, 0.84 * aspect / 0.76)
  return { x: 0.5, y: 0.5, width: height * 0.76 / aspect, height }
}

// Nose displacement in cheek-widths makes the movement independent of distance.
export function faceYaw(landmarks) {
  const left = landmarks[234]?.x
  const right = landmarks[454]?.x
  const span = Math.abs(right - left)
  return span > 0 ? (landmarks[1]?.x - (left + right) / 2) / span : NaN
}

export function selfieFraming(landmarks, guide) {
  const yaw = faceYaw(landmarks)
  if (!Number.isFinite(yaw)) return 'searching'
  const width = Math.abs(landmarks[234].x - landmarks[454].x)
  const height = landmarks[152]?.y - landmarks[10]?.y
  if (!(height > 0)) return 'searching'
  if (width > guide.width * 0.9 || height > guide.height * 0.9) return 'tooClose'
  // Leave a margin for the forehead and chin inside the visible oval.
  const rx = guide.width * 0.47
  const ry = guide.height * 0.47
  const inside = landmarks.every(({ x, y }) =>
    ((x - guide.x) / rx) ** 2 + ((y - guide.y) / ry) ** 2 <= 1
  )
  const cx = (landmarks[234].x + landmarks[454].x) / 2
  const cy = (landmarks[10].y + landmarks[152].y) / 2
  if (!inside || Math.abs(cx - guide.x) > guide.width * 0.22 ||
      Math.abs(cy - guide.y) > guide.height * 0.22) return 'offCentre'
  if (Math.abs(yaw) > 0.14) return 'turnForward'
  if (height < guide.height * 0.30 || width < guide.width * 0.24) return 'tooFar'
  return 'ready'
}
