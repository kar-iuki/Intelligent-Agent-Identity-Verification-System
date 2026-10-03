export function getPasskeyConfig(env = process.env) {
  const rpID = env.WEBAUTHN_RP_ID;
  const rpName = env.WEBAUTHN_RP_NAME;
  const origins = (env.WEBAUTHN_ORIGINS || '').split(',').map(s => s.trim()).filter(Boolean);
  if (!rpID || !rpName || !origins.length || /[:/]/.test(rpID)) throw new Error('Passkeys are not configured');
  for (const origin of origins) {
    const url = new URL(origin);
    if (url.origin !== origin || (url.protocol !== 'https:' && !(url.protocol === 'http:' && url.hostname === 'localhost'))
      || !(url.hostname === rpID || url.hostname.endsWith(`.${rpID}`))) throw new Error('Invalid passkey origin configuration');
  }
  return { rpID, rpName, origins };
}
