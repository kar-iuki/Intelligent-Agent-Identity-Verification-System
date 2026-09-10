import { Router } from 'express'
import authMiddleware from '../middleware/authMiddleware.js'
import { requireRole } from '../middleware/roleMiddleware.js'
import {
  uploadAgentDocuments,
  handleMulterError,
} from '../middleware/uploadMiddleware.js'
import {
  submitRegistration,
  uploadDocuments,
  getAgentProfile,
  getRegistrationStatus,
} from '../controllers/agentController.js'

const router = Router()

router.use(authMiddleware, requireRole('agent'))

router.post('/registration', submitRegistration)
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

export default router
