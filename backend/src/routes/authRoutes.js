import { Router } from 'express'
import authMiddleware from '../middleware/authMiddleware.js'
import passkeyRoutes from './passkeyRoutes.js'
import {
  registerAgent,
  resendVerificationEmail,
  login,
  logout,
  getMe,
  completeOAuthProfile,
} from '../controllers/authController.js'

const router = Router()

router.post('/register', registerAgent)
router.post('/resend-verification', resendVerificationEmail)
router.post('/login', login)
router.post('/logout', authMiddleware, logout)
router.get('/me', authMiddleware, getMe)
router.post('/complete-profile', authMiddleware, completeOAuthProfile)
// Only passkey paths enter the passkey origin/rate-limit middleware.
router.use((req, res, next) => {
  if (/^\/passkeys?(\/|$)/.test(req.path)) return passkeyRoutes(req, res, next)
  next()
})

export default router
