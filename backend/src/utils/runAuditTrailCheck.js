/**
 * CLI helper: node src/utils/runAuditTrailCheck.js <agentID>
 */
import { verifyAuditTrail } from './auditTrailVerifier.js'

const agentID = process.argv[2]

if (!agentID) {
  console.error('Usage: node src/utils/runAuditTrailCheck.js <agentID>')
  process.exit(1)
}

try {
  const report = await verifyAuditTrail(agentID)
  console.log(JSON.stringify(report, null, 2))
  process.exit(report.complete ? 0 : 2)
} catch (err) {
  console.error(err.message || err)
  process.exit(1)
}
