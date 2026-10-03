import { randomBytes } from 'node:crypto';
import * as webauthn from '@simplewebauthn/server';
import { UAParser } from 'ua-parser-js';

export class PasskeyError extends Error {
  constructor(code = 'PASSKEY_FAILED', status = 400) { super(code); this.code = code; this.status = status; }
}
const checked = ({ data, error }) => { if (error) throw new Error('Passkey storage unavailable'); return data; };
export const publicFields = 'id,credential_id,label,browser,os,device_name,created_at,last_used_at,backed_up';

// Dependencies are injectable so tests exercise the actual security orchestration.
export function createPasskeyService({ db, config, issueSession, audit, verifier = webauthn, now = Date.now }) {
  const list = async userId => checked(await db.from('passkeys').select(publicFields).eq('user_id', userId).order('created_at'));
  async function saveChallenge(options, purpose, userId = null) {
    const row = checked(await db.from('passkey_challenges').insert({ challenge: options.challenge, purpose, user_id: userId }).select('id').single());
    return { options, challengeId: row.id };
  }
  async function consume(id, purpose, userId = null) {
    if (typeof id !== 'string' || !/^[0-9a-f-]{36}$/i.test(id)) throw new PasskeyError();
    const rows = checked(await db.rpc('consume_passkey_challenge', { challenge_id: id }));
    const row = rows?.[0];
    if (!row) throw new PasskeyError('CHALLENGE_EXPIRED', 409);
    if (row.purpose !== purpose || row.user_id !== userId) throw new PasskeyError();
    if (Date.parse(row.expires_at) <= now()) throw new PasskeyError('CHALLENGE_EXPIRED', 409);
    return row.challenge;
  }
  return {
    list,
    async loginOptions() {
      return saveChallenge(await verifier.generateAuthenticationOptions({ rpID: config.rpID, challenge: randomBytes(32), allowCredentials: [], userVerification: 'required', timeout: 300000 }), 'login');
    },
    async registerOptions(user, manage = false) {
      const record = checked(await db.from('users').select('webauthn_user_handle,email').eq('user_id', user.id).single());
      const existing = await list(user.id);
      const options = await verifier.generateRegistrationOptions({ rpID: config.rpID, rpName: config.rpName,
        challenge: randomBytes(32), userID: new TextEncoder().encode(record.webauthn_user_handle),
        userName: record.email, userDisplayName: user.suggestedFullName || record.email,
        attestationType: 'none', timeout: 300000,
        excludeCredentials: existing.map(p => ({ id: p.credential_id })),
        authenticatorSelection: { residentKey: 'required', userVerification: 'required', ...(manage ? {} : { authenticatorAttachment: 'platform' }) },
      });
      return saveChallenge(options, 'register', user.id);
    },
    async registerVerify(user, body, ua) {
      const challenge = await consume(body.challengeId, 'register', user.id);
      const result = await verifier.verifyRegistrationResponse({ response: body.response, expectedChallenge: challenge,
        expectedOrigin: config.origins, expectedRPID: config.rpID, requireUserVerification: true });
      if (!result.verified || !result.registrationInfo?.userVerified) throw new PasskeyError();
      const { credential, credentialDeviceType, credentialBackedUp } = result.registrationInfo;
      const parsed = UAParser(String(ua || '').slice(0, 2048));
      const browser = parsed.browser.name || 'Unknown browser';
      const os = parsed.os.name || 'Unknown OS';
      const device = parsed.device.model || parsed.os.name || 'Unknown device';
      const row = checked(await db.from('passkeys').insert({ user_id: user.id, credential_id: credential.id,
        public_key: Buffer.from(credential.publicKey).toString('base64url'), counter: credential.counter,
        transports: credential.transports || [], device_type: credentialDeviceType, backed_up: credentialBackedUp,
        label: `${device} · ${browser}`.slice(0, 100), user_agent: String(ua || '').slice(0, 2048), browser, os, device_name: device,
      }).select(publicFields).single());
      await audit('PASSKEY_REGISTERED', user.id);
      return row;
    },
    async loginVerify(body) {
      const challenge = await consume(body.challengeId, 'login');
      const credential = checked(await db.from('passkeys').select('*').eq('credential_id', body.response?.id || '').maybeSingle());
      if (!credential) throw new PasskeyError();
      const user = checked(await db.from('users').select('webauthn_user_handle').eq('user_id', credential.user_id).single());
      if (body.response?.response?.userHandle !== Buffer.from(user.webauthn_user_handle).toString('base64url')) throw new PasskeyError();
      let result;
      try {
        result = await verifier.verifyAuthenticationResponse({ response: body.response, expectedChallenge: challenge,
          expectedOrigin: config.origins, expectedRPID: config.rpID, requireUserVerification: true,
          credential: { id: credential.credential_id, publicKey: new Uint8Array(Buffer.from(credential.public_key, 'base64url')),
            counter: Number(credential.counter), transports: credential.transports },
        });
      } catch (error) {
        if (/counter/i.test(error.message)) await audit('PASSKEY_COUNTER_REJECTED', credential.user_id, false);
        throw new PasskeyError();
      }
      if (!result.verified || !result.authenticationInfo?.userVerified) throw new PasskeyError();
      const info = result.authenticationInfo;
      if ((info.newCounter > 0 || credential.counter > 0) && info.newCounter <= Number(credential.counter)) {
        await audit('PASSKEY_COUNTER_REJECTED', credential.user_id, false);
        throw new PasskeyError();
      }
      // Compare-and-swap also rejects races against another successful assertion.
      const updated = checked(await db.from('passkeys').update({ counter: info.newCounter, backed_up: info.credentialBackedUp,
        last_used_at: new Date(now()).toISOString() }).eq('id', credential.id).eq('counter', credential.counter).select('id'));
      if (!updated.length) throw new PasskeyError();
      const session = await issueSession(credential.user_id);
      await audit('PASSKEY_LOGIN_SUCCESS', credential.user_id);
      return { ...session, credentialId: credential.credential_id };
    },
    async rename(userId, id, label) {
      if (typeof label !== 'string' || !label.trim() || label.trim().length > 100) throw new PasskeyError('INVALID_LABEL');
      const row = checked(await db.from('passkeys').update({ label: label.trim() }).eq('id', id).eq('user_id', userId).select(publicFields).maybeSingle());
      if (!row) throw new PasskeyError('NOT_FOUND', 404);
      return row;
    },
    async remove(userId, id) {
      const result = checked(await db.rpc('remove_passkey', { owner_id: userId, passkey_id: id }));
      if (result === 'not_found') throw new PasskeyError('NOT_FOUND', 404);
      if (result === 'last_method') throw new PasskeyError('LAST_LOGIN_METHOD', 409);
      if (result !== 'removed') throw new Error('Passkey removal failed');
      await audit('PASSKEY_REMOVED', userId);
    },
  };
}
