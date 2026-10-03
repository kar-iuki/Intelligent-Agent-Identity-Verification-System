import test from 'node:test';
import assert from 'node:assert/strict';
import * as webauthn from '@simplewebauthn/server';
import { createPasskeyService } from '../src/services/passkeyService.js';
import { getPasskeyConfig } from '../src/config/passkeyConfig.js';
import { memoryDb } from './helpers/passkeyMemoryDb.js';
const config = { rpID:'localhost', rpName:'Test agents', origins:['http://localhost:5178'] };
function fixture(overrides = {}) {
  const db = memoryDb(), events = [], sessions = [];
  const user = { id:'11111111-1111-1111-1111-111111111111' };
  db.tables.users.push({ user_id:user.id, email:'agent@example.test', webauthn_user_handle:'opaque-handle', recovery:true });
  db.tables.passkeys.push({ id:'22222222-2222-2222-2222-222222222222', user_id:user.id, credential_id:'Y3JlZGVudGlhbA', public_key:'AA', counter:0 });
  const verifier = { ...webauthn, verifyAuthenticationResponse:async () => ({ verified:true, authenticationInfo:{ userVerified:true, newCounter:1 } }),
    verifyRegistrationResponse:async () => ({ verified:true, registrationInfo:{ userVerified:true, credential:{ id:'bmV3', publicKey:new Uint8Array([1]), counter:0, transports:['internal'] }, credentialDeviceType:'multiDevice', credentialBackedUp:true } }), ...overrides };
  const service = createPasskeyService({ db, config, verifier, issueSession:async id => { sessions.push(id); return { token:'normal-supabase-token', user:{ user_id:id } }; }, audit:async (...event) => events.push(event) });
  const response = { id:'Y3JlZGVudGlhbA', response:{ userHandle:Buffer.from('opaque-handle').toString('base64url') } };
  return { service, db, user, response, events, sessions };
}
test('origin config fails closed and allows only HTTPS or localhost', () => {
  assert.deepEqual(getPasskeyConfig({ WEBAUTHN_RP_ID:'localhost', WEBAUTHN_RP_NAME:'Agents', WEBAUTHN_ORIGINS:'http://localhost:5178' }).origins, config.origins);
  for (const origins of ['http://example.com','https://evil.test','https://example.com/path']) assert.throws(() => getPasskeyConfig({ WEBAUTHN_RP_ID:'example.com', WEBAUTHN_RP_NAME:'Agents', WEBAUTHN_ORIGINS:origins }));
  assert.throws(() => getPasskeyConfig({}));
});
test('options have random 32-byte challenges, discoverable login, UV, opaque handle, exclusion and attachment policy', async () => {
  const { service, user, db } = fixture();
  const first = await service.loginOptions(), second = await service.loginOptions();
  assert.notEqual(first.options.challenge, second.options.challenge);
  assert.ok(Buffer.from(first.options.challenge,'base64url').length >= 32);
  assert.deepEqual(first.options.allowCredentials, []); assert.equal(first.options.userVerification,'required');
  assert.equal(db.tables.passkey_challenges[0].user_id,null);
  const prompt = (await service.registerOptions(user)).options;
  assert.equal(prompt.authenticatorSelection.residentKey,'required'); assert.equal(prompt.authenticatorSelection.userVerification,'required');
  assert.equal(prompt.authenticatorSelection.authenticatorAttachment,'platform'); assert.equal(prompt.attestation,'none');
  assert.equal(Buffer.from(prompt.user.id,'base64url').toString(),'opaque-handle'); assert.equal(prompt.excludeCredentials.length,1);
  assert.equal((await service.registerOptions(user,true)).options.authenticatorSelection.authenticatorAttachment,undefined);
});
test('successful login consumes challenge, checks verifier arguments, updates counter and issues normal session', async () => {
  let args;
  const { service, db, response, sessions } = fixture({ verifyAuthenticationResponse:async input => { args = input; return { verified:true, authenticationInfo:{ userVerified:true, newCounter:2 } }; } });
  const options = await service.loginOptions();
  const result = await service.loginVerify({ challengeId:options.challengeId, response });
  assert.equal(result.token,'normal-supabase-token'); assert.equal(args.requireUserVerification,true); assert.equal(args.expectedRPID,'localhost'); assert.deepEqual(args.expectedOrigin,config.origins);
  assert.equal(db.tables.passkeys[0].counter,2); assert.ok(db.tables.passkeys[0].last_used_at); assert.equal(sessions.length,1);
  await assert.rejects(service.loginVerify({ challengeId:options.challengeId, response })); assert.equal(sessions.length,1);
});
test('failed assertions consume challenges and never issue sessions', async () => {
  for (const verifyAuthenticationResponse of [async () => { throw Error('bad signature'); }, async () => ({ verified:false }), async () => ({ verified:true, authenticationInfo:{ userVerified:false } })]) {
    const { service, response, sessions, db } = fixture({ verifyAuthenticationResponse });
    const { challengeId } = await service.loginOptions(); await assert.rejects(service.loginVerify({ challengeId, response }));
    assert.equal(db.tables.passkey_challenges.length,0); assert.equal(sessions.length,0);
  }
});
test('expired, wrong-user and wrong-purpose challenges fail; userHandle binds the account', async () => {
  const { service, response, user, db } = fixture();
  const expired = await service.loginOptions(); db.tables.passkey_challenges[0].expires_at = new Date(0).toISOString();
  await assert.rejects(service.loginVerify({ challengeId:expired.challengeId, response }), { code:'CHALLENGE_EXPIRED' });
  const registration = await service.registerOptions(user);
  await assert.rejects(service.registerVerify({ id:'different' }, { challengeId:registration.challengeId, response }));
  const wrongPurpose = await service.registerOptions(user); await assert.rejects(service.loginVerify({ challengeId:wrongPurpose.challengeId, response }));
  const wrongUser = await service.loginOptions(); await assert.rejects(service.loginVerify({ challengeId:wrongUser.challengeId, response:{ ...response, response:{ userHandle:'wrong' } } }));
});
test('counter regression rejects and logs; synced zero counters work', async () => {
  const { service, db, response, events } = fixture(); db.tables.passkeys[0].counter = 5;
  const options = await service.loginOptions(); await assert.rejects(service.loginVerify({ challengeId:options.challengeId, response }));
  assert.equal(events[0][0],'PASSKEY_COUNTER_REJECTED'); assert.equal(db.tables.passkeys[0].counter,5);
  const zero = fixture({ verifyAuthenticationResponse:async () => ({ verified:true, authenticationInfo:{ userVerified:true, newCounter:0 } }) });
  await zero.service.loginVerify({ challengeId:(await zero.service.loginOptions()).challengeId, response:zero.response });
  assert.equal(zero.sessions.length,1);
});
test('registration stores only verified credentials, parses UA, and rejects duplicate and replay', async () => {
  const { service, user, db } = fixture(); const options = await service.registerOptions(user);
  const row = await service.registerVerify(user, { challengeId:options.challengeId, response:{} }, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36');
  assert.equal(row.browser,'Chrome'); assert.equal(row.backed_up,true); assert.equal(db.tables.passkeys.length,2);
  await assert.rejects(service.registerVerify(user, { challengeId:options.challengeId, response:{} }));
  await assert.rejects(service.registerVerify(user, { challengeId:(await service.registerOptions(user)).challengeId, response:{} }));
  const failed = fixture({ verifyRegistrationResponse:async () => ({ verified:false }) });
  await assert.rejects(failed.service.registerVerify(failed.user, { challengeId:(await failed.service.registerOptions(failed.user)).challengeId, response:{} }));
});
test('management scopes rename/delete and protects last method', async () => {
  const { service, db, user } = fixture(); const id = db.tables.passkeys[0].id;
  await assert.rejects(service.remove('another-user',id), { code:'NOT_FOUND' });
  await assert.rejects(service.rename('another-user',id,'Name'), { code:'NOT_FOUND' });
  await assert.rejects(service.rename(user.id,id,' '), { code:'INVALID_LABEL' });
  assert.equal((await service.rename(user.id,id,'My laptop')).label,'My laptop');
  db.tables.users[0].recovery = false; await assert.rejects(service.remove(user.id,id), { code:'LAST_LOGIN_METHOD' });
  db.tables.users[0].recovery = true; await service.remove(user.id,id); assert.equal(db.tables.passkeys.length,0);
});
