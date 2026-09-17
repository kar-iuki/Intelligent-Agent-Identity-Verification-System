import 'dotenv/config'
import http from 'http'
import express from 'express'
import cors from 'cors'
import helmet from 'helmet'
import { Server } from 'socket.io'
import authRoutes from './src/routes/authRoutes.js'
import agentRoutes from './src/routes/agentRoutes.js'
import verificationRoutes from './src/routes/verificationRoutes.js'
import adminRoutes from './src/routes/adminRoutes.js'
import { startReviewCaseRealtime } from './src/services/realtimeService.js'
import requestLogger from './src/middleware/requestLogger.js'
import { isFraudConfigValid } from './src/config/fraudConfig.js'

isFraudConfigValid()

const app = express()
const PORT = process.env.PORT || 3000

/** Allow localhost + comma-separated FRONTEND_URL values (LAN / ngrok testing). */
function parseAllowedOrigins() {
  const defaults = ['http://localhost:5173', 'http://127.0.0.1:5173']
  const fromEnv = String(process.env.FRONTEND_URL || '')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
  return [...new Set([...defaults, ...fromEnv])]
}

const allowedOrigins = parseAllowedOrigins()

function corsOrigin(origin, callback) {
  if (!origin || allowedOrigins.includes(origin)) {
    return callback(null, true)
  }
  return callback(new Error(`CORS blocked for origin: ${origin}`))
}

const server = http.createServer(app)
const io = new Server(server, {
  cors: {
    origin: allowedOrigins,
    methods: ['GET', 'POST'],
  },
})

app.set('io', io)

app.use(helmet({
  crossOriginResourcePolicy: { policy: 'cross-origin' },
}))
app.use(cors({
  origin: corsOrigin,
}))
app.set('trust proxy', 1)
app.use(express.json())
app.use(express.urlencoded({ extended: true }))
app.use(requestLogger)

app.get('/health', (_req, res) => {
  res.json({ status: 'ok' })
})

app.use('/api/auth', authRoutes)
app.use('/api/agent', agentRoutes)
app.use('/api/verification', verificationRoutes)
app.use('/api/admin', adminRoutes)

io.on('connection', (socket) => {
  console.log(`Socket connected: ${socket.id}`)
  socket.on('disconnect', () => {
    console.log(`Socket disconnected: ${socket.id}`)
  })
})

startReviewCaseRealtime(io)

server.listen(PORT, '0.0.0.0', () => {
  console.log(`Backend server running on port ${PORT}`)
  console.log(`Allowed frontend origins: ${allowedOrigins.join(', ')}`)
})
