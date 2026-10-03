import { Router } from 'express';
import { createHash } from 'node:crypto';
import { createClient } from '@supabase/supabase-js';
import db from '../utils/supabaseClient.js';
import authMiddleware, { requireCompleteProfile } from '../middleware/authMiddleware.js';
import { buildAuthSession } from '../controllers/authController.js';
import { createPasskeyService, PasskeyError } from '../services/passkeyService.js';
import { getPasskeyConfig } from '../config/passkeyConfig.js';
import { logAction } from '../utils/auditLogger.js';

export function createPasskeyRouter({ database = db, authenticate = authMiddleware, readConfig = getPasskeyConfig, sessionIssuer, logger = logAction } = {}) {
const router = Router();
router.use(async (req, res, next) => {
  res.set('Cache-Control', 'no-store');
  try { req.passkeyConfig = readConfig(); } catch { return res.status(503).json({ error: 'Passkeys are not available yet.' }); }
  // Tokens are explicit Bearer headers, never ambient cookies. Also require an
  // allowed Origin on all passkey requests, including unauthenticated ceremonies.
  // Same-origin GETs commonly omit Origin. The read-only list still requires
  // Bearer authentication below; all writes require an explicit allowed Origin.
  const sameOriginRead = req.method === 'GET' && !req.get('Origin');
  if (!sameOriginRead && !req.passkeyConfig.origins.includes(req.get('Origin'))) return res.status(403).json({ error: 'Request not allowed.' });
  try {
    const bucket = createHash('sha256').update(`${req.ip}:passkeys`).digest('hex');
    const { data, error } = await database.rpc('passkey_rate_limit', { rate_bucket: bucket, max_attempts: 60 });
    if (error) throw error;
    if (!data) return res.status(429).set('Retry-After', '300').json({ error: 'Please wait a few minutes and try again.' });
    next();
  } catch { res.status(503).json({ error: 'Passkeys are temporarily unavailable. Please try again.' }); }
});

function service(req) {
  return createPasskeyService({ db: database, config: req.passkeyConfig,
    audit: (action, userId, success = true) => logger({ action, performedBy: userId || 'system', outcome: success ? 'SUCCESS' : 'FAILED', ipAddress: req.clientIP }),
    issueSession: sessionIssuer || (async userId => {
      const { data: account, error: accountError } = await db.auth.admin.getUserById(userId);
      if (accountError || !account?.user?.email || !account.user.email_confirmed_at) throw new PasskeyError();
      // No email is sent. Exchange a server-only one-time token only AFTER a
      // verified assertion; never expose the link/token or accept a client email.
      const { data: link, error } = await db.auth.admin.generateLink({ type: 'magiclink', email: account.user.email });
      if (error || link?.user?.id !== userId) throw new PasskeyError();
      const client = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_ANON_KEY, { auth: { persistSession: false, autoRefreshToken: false } });
      const { data, error: exchangeError } = await client.auth.verifyOtp({ token_hash: link.properties.hashed_token, type: 'magiclink' });
      if (exchangeError || data.user?.id !== userId || !data.session) throw new PasskeyError();
      return buildAuthSession(data, req);
    }),
  });
}
const messages = {
  CHALLENGE_EXPIRED: 'That request expired. Please try again.',
  LAST_LOGIN_METHOD: 'Add a password or another login method before removing your last passkey.',
  INVALID_LABEL: 'Use a name between 1 and 100 characters.',
  NOT_FOUND: 'Passkey not found.',
};
const run = fn => async (req, res) => {
  try { await fn(req, res, service(req)); }
  catch (error) {
    if (req.path === '/passkey/login/verify') await logger({ action: 'PASSKEY_LOGIN_FAILED', outcome: 'FAILED', performedBy: 'system', ipAddress: req.clientIP });
    const known = error instanceof PasskeyError;
    res.status(known ? error.status : 400).json({ code: known ? error.code : 'PASSKEY_FAILED', error: messages[error.code] || 'Could not complete passkey sign-in or setup. Please try again.' });
  }
};
router.post('/passkey/login/options', run(async (_req, res, s) => res.json(await s.loginOptions())));
router.post('/passkey/login/verify', run(async (req, res, s) => res.json(await s.loginVerify(req.body))));
router.use(authenticate, requireCompleteProfile);
router.post('/passkey/register/options', run(async (req, res, s) => res.json(await s.registerOptions(req.user, req.body?.manage === true))));
router.post('/passkey/register/verify', run(async (req, res, s) => res.status(201).json(await s.registerVerify(req.user, req.body, req.get('User-Agent')))));
router.get('/passkeys', run(async (req, res, s) => res.json({ passkeys: await s.list(req.user.id), rpId: req.passkeyConfig.rpID })));
router.patch('/passkeys/:id', run(async (req, res, s) => res.json(await s.rename(req.user.id, req.params.id, req.body?.label))));
router.delete('/passkeys/:id', run(async (req, res, s) => { await s.remove(req.user.id, req.params.id); res.sendStatus(204); }));
return router;
}
export default createPasskeyRouter();
