import { randomBytes, randomInt, timingSafeEqual } from 'node:crypto'

const ALPHABET = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'
const TTL_MS = 5 * 60 * 1000
const MAX_CHALLENGES = 2000
const challenges = new Map()

// 5×7 glyphs. Bits are left-to-right so the answer is never written as text.
const GLYPHS = {
  A: [0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
  B: [0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110],
  C: [0b01111, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b01111],
  D: [0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110],
  E: [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111],
  F: [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000],
  G: [0b01111, 0b10000, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111],
  H: [0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
  J: [0b00111, 0b00001, 0b00001, 0b00001, 0b10001, 0b10001, 0b01110],
  K: [0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001],
  M: [0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001],
  N: [0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001],
  P: [0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000],
  Q: [0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101],
  R: [0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001],
  S: [0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110],
  T: [0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
  U: [0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
  V: [0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100],
  W: [0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b10101, 0b01010],
  X: [0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001],
  Y: [0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100],
  Z: [0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111],
  2: [0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0b01000, 0b11111],
  3: [0b11110, 0b00001, 0b00001, 0b01110, 0b00001, 0b00001, 0b11110],
  4: [0b00001, 0b00011, 0b00101, 0b01001, 0b11111, 0b00001, 0b00001],
  5: [0b11111, 0b10000, 0b10000, 0b11110, 0b00001, 0b00001, 0b11110],
  6: [0b01110, 0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110],
  7: [0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000],
  8: [0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110],
  9: [0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00001, 0b01110],
}

function prune(now = Date.now()) {
  for (const [id, row] of challenges) {
    if (row.expires <= now) challenges.delete(id)
  }
  while (challenges.size > MAX_CHALLENGES) {
    challenges.delete(challenges.keys().next().value)
  }
}

function randomAnswer() {
  return Array.from({ length: 5 }, () => ALPHABET[randomInt(ALPHABET.length)]).join('')
}

function renderSvg(answer) {
  const scale = 4
  const width = 210
  const height = 68
  const pixels = []
  answer.split('').forEach((char, index) => {
    const glyph = GLYPHS[char]
    const originX = 16 + index * 38 + randomInt(3)
    const originY = 14 + randomInt(7)
    glyph.forEach((row, y) => {
      for (let x = 0; x < 5; x += 1) {
        if ((row & (1 << (4 - x))) === 0) continue
        pixels.push(`<rect x="${originX + x * scale}" y="${originY + y * scale}" width="${scale - 0.4}" height="${scale - 0.4}" fill="#173b2d"/>`)
      }
    })
  })
  const noise = []
  for (let i = 0; i < 7; i += 1) {
    noise.push(`<line x1="${randomInt(width)}" y1="${randomInt(height)}" x2="${randomInt(width)}" y2="${randomInt(height)}" stroke="#8eae98" stroke-width="1"/>`)
  }
  for (let i = 0; i < 28; i += 1) {
    noise.push(`<circle cx="${randomInt(width)}" cy="${randomInt(height)}" r="${randomInt(2) + 0.6}" fill="#9db8a4"/>`)
  }
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img"><rect width="100%" height="100%" rx="8" fill="#f3f7f1"/>${noise.join('')}${pixels.join('')}</svg>`
}

export function createCaptcha(options = {}) {
  prune()
  const answer = options.answer || randomAnswer()
  if (!GLYPHS[answer[0]] || answer.length !== 5 || [...answer].some((char) => !GLYPHS[char])) {
    throw new Error('Captcha answer is not displayable')
  }
  const id = randomBytes(16).toString('hex')
  challenges.set(id, { answer, expires: Date.now() + TTL_MS })
  return { id, svg: renderSvg(answer) }
}

export function verifyCaptcha(id, attempt) {
  prune()
  if (typeof id !== 'string' || !/^[a-f0-9]{32}$/.test(id)) return false
  const row = challenges.get(id)
  if (!row) return false
  challenges.delete(id)
  if (row.expires <= Date.now()) return false
  const given = String(attempt || '').trim().toUpperCase()
  if (given.length !== row.answer.length) return false
  return timingSafeEqual(Buffer.from(given), Buffer.from(row.answer))
}
