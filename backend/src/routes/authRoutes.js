import { Router } from 'express'
import authMiddleware from '../middleware/authMiddleware.js'
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

export default router
