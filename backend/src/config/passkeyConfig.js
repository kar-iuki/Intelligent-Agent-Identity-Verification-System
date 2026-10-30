export function getPasskeyConfig(env = process.env) {
  // Only use deployment-owned settings, never Origin/Host request headers.
  const origins = (env.WEBAUTHN_ORIGINS || env.FRONTEND_URL || '').split(',').map(s => s.trim()).filter(Boolean);
  const hosts = [...new Set(origins.map(origin => new URL(origin).hostname))];
  const rpID = env.WEBAUTHN_RP_ID || (hosts.length === 1 ? hosts[0] : null);
  const rpName = env.WEBAUTHN_RP_NAME || 'Agent Identity Verification';
  if (!rpID || !rpName || !origins.length || /[:/]/.test(rpID)) throw new Error('Passkeys are not configured');
  for (const origin of origins) {
    const url = new URL(origin);
    if (url.origin !== origin || (url.protocol !== 'https:' && !(url.protocol === 'http:' && url.hostname === 'localhost'))
      || !(url.hostname === rpID || url.hostname.endsWith(`.${rpID}`))) throw new Error('Invalid passkey origin configuration');
  }
  return { rpID, rpName, origins };
}
