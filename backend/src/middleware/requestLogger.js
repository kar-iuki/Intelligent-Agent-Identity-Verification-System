/**
 * Attach client IP to every request as req.clientIP.
 */
export default function requestLogger(req, _res, next) {
  const forwarded = req.headers['x-forwarded-for']
  let clientIP = null

  if (typeof forwarded === 'string' && forwarded.trim()) {
    clientIP = forwarded.split(',')[0].trim()
  } else if (Array.isArray(forwarded) && forwarded.length > 0) {
    clientIP = String(forwarded[0]).trim()
  } else if (req.connection?.remoteAddress) {
    clientIP = req.connection.remoteAddress
  } else if (req.socket?.remoteAddress) {
    clientIP = req.socket.remoteAddress
  } else if (req.ip) {
    clientIP = req.ip
  }

  req.clientIP = clientIP
  next()
}
