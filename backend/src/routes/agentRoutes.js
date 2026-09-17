import { Router } from 'express'
import authMiddleware from '../middleware/authMiddleware.js'
import { requireRole } from '../middleware/roleMiddleware.js'
import fraudGuardrailsMiddleware from '../middleware/fraudGuardrailsMiddleware.js'
import {
  uploadAgentDocuments,
  uploadSingleImage,
  handleMulterError,
} from '../middleware/uploadMiddleware.js'
import {
  submitRegistration,
  uploadDocuments,
  checkImageQuality,
  getAgentProfile,
  getRegistrationStatus,
  getAgentAuditLogs,
} from '../controllers/agentController.js'

const router = Router()

router.use(authMiddleware, requireRole('agent'))

router.post('/registration', fraudGuardrailsMiddleware, submitRegistration)
router.post(
  '/documents/quality-check',
  (req, res, next) => {
    uploadSingleImage(req, res, (err) => {
      if (err) return handleMulterError(err, req, res, next)
      next()
    })
  },
  checkImageQuality
)
router.post(
  '/documents',
  (req, res, next) => {
    uploadAgentDocuments(req, res, (err) => {
      if (err) return handleMulterError(err, req, res, next)
      next()
    })
  },
  uploadDocuments
)
router.get('/profile', getAgentProfile)
router.get('/registration/status', getRegistrationStatus)
router.get('/audit', getAgentAuditLogs)

export default router
