import { Router } from 'express'
import authMiddleware from '../middleware/authMiddleware.js'
import { requireRole } from '../middleware/roleMiddleware.js'
import { initiateVerification } from '../controllers/verificationController.js'

const router = Router()

router.post(
  '/initiate',
  authMiddleware,
  requireRole('agent'),
  initiateVerification
)

export default router
