import { randomBytes } from 'node:crypto';
import * as webauthn from '@simplewebauthn/server';
import { UAParser } from 'ua-parser-js';

export class PasskeyError extends Error {
  constructor(code = 'PASSKEY_FAILED', status = 400) { super(code); this.code = code; this.status = status; }
}
const checked = ({ data, error }) => { if (error) throw new Error('Passkey storage unavailable'); return data; };
export const publicFields = 'id,credential_id,label,browser,os,device_name,created_at,last_used_at,backed_up';
const handleBytes = value => Buffer.from(String(value)).toString('base64url');
const allowCredential = row => ({ id: row.credential_id, ...(Array.isArray(row.transports) && row.transports.length ? { transports: row.transports } : {}) });

// Dependencies are injectable so tests exercise the actual security orchestration.
export function createPasskeyService({ db, config, issueSession, audit, verifier = webauthn, now = Date.now }) {
  const list = async userId => checked(await db.from('passkeys').select(publicFields).eq('user_id', userId).order('created_at'));
  async function account(userId) {
    const record = checked(await db.from('users').select('webauthn_user_handle,email').eq('user_id', userId).maybeSingle());
    if (!record?.webauthn_user_handle) return { userHandle: null, userName: null };
    return { userHandle: handleBytes(record.webauthn_user_handle), userName: record.email || null };
  }
  async function hasRecovery(userId) {
    const getUser = db.auth?.admin?.getUserById;
    if (!getUser) return false;
    try {
      const { data, error } = await getUser(userId);
      const user = data?.user;
      if (error || !user) return false;
      if ((user.identities || []).some(identity => identity?.provider)) return true;
      return (user.app_metadata?.providers || []).length > 0;
    } catch { return false; }
  }
  async function targetedCredentials(email, credentialIds) {
    const chosen = new Map();
    const normalized = typeof email === 'string' ? email.trim().toLowerCase() : '';
    if (normalized && normalized.length <= 320) {
      const owner = checked(await db.from('users').select('user_id').eq('email', normalized).maybeSingle());
      if (owner) {
        const rows = checked(await db.from('passkeys').select('credential_id,transports').eq('user_id', owner.user_id));
        for (const row of rows) chosen.set(row.credential_id, row);
      }
    }
    const ids = [...new Set((Array.isArray(credentialIds) ? credentialIds : []).filter(id => typeof id === 'string' && id.length > 0 && id.length <= 512))].slice(0, 10);
    if (ids.length) {
      const rows = checked(await db.from('passkeys').select('credential_id,transports').in('credential_id', ids));
      for (const row of rows) chosen.set(row.credential_id, row);
    }
    return [...chosen.values()].map(allowCredential);
  }
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
    account,
    async loginOptions(hints = {}) {
      // An empty list stays discoverable. A typed email or a credential already
      // saved in this browser is included so the browser can use that passkey
      // before its account chooser has seen a password login.
      const allowCredentials = await targetedCredentials(hints.email, hints.credentialIds);
      return saveChallenge(await verifier.generateAuthenticationOptions({ rpID: config.rpID, challenge: randomBytes(32), allowCredentials, userVerification: 'preferred', timeout: 300000 }), 'login');
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
      // Some authenticators omit userHandle until the passkey has been used.
      // A present handle must still match the account that owns this credential.
      const presented = body.response?.response?.userHandle;
      if (typeof presented === 'string' && presented.length > 0 && presented !== handleBytes(user.webauthn_user_handle)) throw new PasskeyError();
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
      const deleteOwned = async () => {
        const removed = checked(await db.from('passkeys').delete().eq('id', id).eq('user_id', userId).select('id'));
        if (!removed?.length) throw new PasskeyError('NOT_FOUND', 404);
        await audit('PASSKEY_REMOVED', userId);
      };
      let result;
      try { result = checked(await db.rpc('remove_passkey', { owner_id: userId, passkey_id: id })); }
      catch (error) {
        // A password or Google login is enough when the database check cannot read auth.users.
        if (error?.message === 'Passkey storage unavailable' && await hasRecovery(userId)) return deleteOwned();
        throw error;
      }
      if (result === 'removed') { await audit('PASSKEY_REMOVED', userId); return; }
      if (result === 'not_found') throw new PasskeyError('NOT_FOUND', 404);
      if (result === 'last_method' && await hasRecovery(userId)) return deleteOwned();
      if (result === 'last_method') throw new PasskeyError('LAST_LOGIN_METHOD', 409);
      throw new Error('Passkey removal failed');
    },
  };
}
