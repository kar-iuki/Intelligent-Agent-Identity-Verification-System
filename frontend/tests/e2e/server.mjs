// Isolated localhost test API: real production passkey routes + WebAuthn crypto,
// in-memory storage and fake Supabase session boundary. Never loaded by server.js.
import express from '../../../backend/node_modules/express/index.js';
import { memoryDb } from '../../../backend/tests/helpers/passkeyMemoryDb.js';
process.env.SUPABASE_URL = 'http://localhost:54321';
process.env.SUPABASE_SERVICE_ROLE_KEY = 'test-only';
process.env.SUPABASE_ANON_KEY = 'test-only';
const { createPasskeyRouter } = await import('../../../backend/src/routes/passkeyRoutes.js');
const app = express();
app.use(express.json());
const db = memoryDb();
const user = { user_id:'11111111-1111-1111-1111-111111111111', email:'agent@example.test', role:'agent', webauthn_user_handle:'test-opaque-handle', recovery:true };
const agent = { agent_id:'test-agent', full_name:'Test Agent', user_id:user.user_id };
const session = { token:'test-token', user, role:'agent', agent };
db.tables.users.push(user);
app.post('/test/reset', (_req,res) => { db.tables.passkeys.length = 0; db.tables.passkey_challenges.length = 0; db.rates.clear(); res.json({ ok:true }); });
app.get('/health', (_req,res) => res.json({ ok:true }));
app.post('/api/auth/login', (_req,res) => res.json(session));
app.post('/api/auth/logout', (_req,res) => res.json({ ok:true }));
app.get('/api/auth/me', (_req,res) => res.json(session));
app.get('/api/agent/registration/status', (_req,res) => res.json({ status:'verification_pending' }));
app.get('/api/agent/profile', (_req,res) => res.json({ email:user.email, agent }));
app.get('/api/verification/status', (_req,res) => res.json({ status:'verified', isFinal:true }));
app.use('/api/auth', createPasskeyRouter({ database:db, readConfig:() => ({ rpID:'localhost', rpName:'Test agents', origins:['http://localhost:5178'] }),
  authenticate:(req,res,next) => { if (req.get('Authorization') !== 'Bearer test-token') return res.sendStatus(401); req.user = { id:user.user_id, profileComplete:true }; next(); },
  sessionIssuer:async () => session, logger:async () => {},
}));
app.listen(3101,'127.0.0.1');
