import { Router } from 'express'
import authMiddleware from '../middleware/authMiddleware.js'
import { requireRole } from '../middleware/roleMiddleware.js'
import {
  getPendingReviewCases,
  getAllAgents,
  getAgentVerificationDetail,
  approveAgent,
  rejectAgent,
  getAuditLogs,
  getAgentDocumentImages,
  getDashboardStats,
  exportAuditLogs,
  getRecentActivity,
  getAuditLogsByAgent,
  getFlaggedRegistrations,
  resetAgentStrikes,
} from '../controllers/adminController.js'

const router = Router()

router.use(authMiddleware, requireRole('admin'))

router.get('/stats', getDashboardStats)
router.get('/activity/recent', getRecentActivity)
router.get('/fraud/flagged', getFlaggedRegistrations)
router.get('/audit/export', exportAuditLogs)
router.get('/cases/pending', getPendingReviewCases)
router.get('/agents', getAllAgents)
router.get('/agents/:agentID/images', getAgentDocumentImages)
router.get('/agents/:agentID/audit', getAuditLogsByAgent)
router.post('/agents/:agentID/reset-strikes', resetAgentStrikes)
router.get('/agents/:agentID', getAgentVerificationDetail)
router.post('/agents/:agentID/approve', approveAgent)
router.post('/agents/:agentID/reject', rejectAgent)
router.get('/audit-logs', getAuditLogs)

export default router
