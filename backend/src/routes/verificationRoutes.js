import { Router } from 'express'
import authMiddleware from '../middleware/authMiddleware.js'
import { requireRole } from '../middleware/roleMiddleware.js'
import {
  initiateVerification,
  getVerificationStatus,
  getVerificationResult,
} from '../controllers/verificationController.js'

const router = Router()

router.post(
  '/initiate',
  authMiddleware,
  requireRole('agent'),
  initiateVerification
)

router.get(
  '/status',
  authMiddleware,
  requireRole('agent'),
  getVerificationStatus
)

router.get(
  '/result',
  authMiddleware,
  requireRole('agent'),
  getVerificationResult
)

export default router
