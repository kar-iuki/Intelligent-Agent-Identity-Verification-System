import 'dotenv/config'
import express from 'express'
import cors from 'cors'
import helmet from 'helmet'
import authRoutes from './src/routes/authRoutes.js'
import agentRoutes from './src/routes/agentRoutes.js'
import verificationRoutes from './src/routes/verificationRoutes.js'

const app = express()
const PORT = process.env.PORT || 3000

app.use(helmet())
app.use(cors())
app.use(express.json())
app.use(express.urlencoded({ extended: true }))

app.get('/health', (_req, res) => {
  res.json({ status: 'ok' })
})

app.use('/api/auth', authRoutes)
app.use('/api/agent', agentRoutes)
app.use('/api/verification', verificationRoutes)

app.listen(PORT, () => {
  console.log(`Backend server running on port ${PORT}`)
})
