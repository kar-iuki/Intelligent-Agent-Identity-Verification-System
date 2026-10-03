import test from 'node:test';
import assert from 'node:assert/strict';
import express from 'express';
import { memoryDb } from './helpers/passkeyMemoryDb.js';
process.env.SUPABASE_URL = 'http://localhost:54321';
process.env.SUPABASE_SERVICE_ROLE_KEY = 'test-only';
process.env.SUPABASE_ANON_KEY = 'test-only';
const { createPasskeyRouter } = await import('../src/routes/passkeyRoutes.js');

test('HTTP endpoints enforce origin, auth, complete profile, generic failures and rate limits', async () => {
  const db = memoryDb(), app = express();
  app.use(express.json());
  app.use('/api/auth',createPasskeyRouter({ database:db, logger:async () => {},
    readConfig:() => ({ rpID:'localhost', rpName:'Test', origins:['http://localhost:5178'] }),
    authenticate:(req,res,next) => {
      if (!req.get('Authorization')) return res.sendStatus(401);
      req.user = { id:'11111111-1111-1111-1111-111111111111', profileComplete:req.get('Authorization') !== 'incomplete' }; next();
    },
  }));
  const server = app.listen(0,'127.0.0.1');
  await new Promise(resolve => server.once('listening',resolve));
  const url = `http://127.0.0.1:${server.address().port}/api/auth`;
  const call = (path, options = {}) => fetch(url + path, { method:'POST', ...options, headers:{ Origin:'http://localhost:5178', 'Content-Type':'application/json', ...options.headers } });
  try {
    assert.equal((await call('/passkey/login/options',{ headers:{ Origin:'https://evil.test' } })).status,403);
    assert.equal((await call('/passkey/register/options')).status,401);
    assert.equal((await call('/passkey/register/options',{ headers:{ Authorization:'incomplete' } })).status,403);
    assert.equal((await call('/passkeys/id',{ method:'DELETE' })).status,401);
    const list = await fetch(url + '/passkeys', { headers:{ Authorization:'Bearer test' } });
    assert.equal(list.status,200); // Same-origin browser GET has no Origin header.
    const first = await call('/passkey/login/options'); assert.equal(first.status,200); assert.equal(first.headers.get('cache-control'),'no-store');
    const unknown = await call('/passkey/login/verify',{ body:JSON.stringify({ challengeId:'not-valid', response:{ id:'unknown' } }) });
    assert.equal(unknown.status,400); assert.equal((await unknown.json()).code,'PASSKEY_FAILED');
    db.rates.clear();
    for (let i = 0; i < 60; i++) assert.equal((await call('/passkey/login/options')).status,200);
    for (const path of ['/passkey/login/options','/passkey/login/verify','/passkey/register/options','/passkey/register/verify','/passkeys']) {
      const blocked = await call(path); assert.equal(blocked.status,429); assert.equal(blocked.headers.get('retry-after'),'300');
    }
  } finally { await new Promise(resolve => server.close(resolve)); }
});
