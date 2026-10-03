import { randomUUID } from 'node:crypto';

// Test double for storage only. Browser tests use real SimpleWebAuthn crypto.
export function memoryDb() {
  const tables = { users: [], passkeys: [], passkey_challenges: [] };
  const rates = new Map();
  return {
    tables, rates,
    from(table) {
      let action = 'select', payload, single = false;
      const filters = [];
      const query = {
        select() { return query; }, order() { return query; },
        eq(key, value) { filters.push(row => row[key] === value); return query; },
        insert(value) { action = 'insert'; payload = value; return query; },
        update(value) { action = 'update'; payload = value; return query; },
        single() { single = true; return query; }, maybeSingle() { single = true; return query; },
        then(resolve) {
          let rows = tables[table].filter(row => filters.every(f => f(row)));
          if (action === 'insert') {
            if (table === 'passkeys' && tables.passkeys.some(p => p.credential_id === payload.credential_id)) return Promise.resolve({ error: { message:'duplicate' } }).then(resolve);
            const row = { id:randomUUID(), created_at:new Date().toISOString(), expires_at:new Date(Date.now() + 300000).toISOString(), ...payload };
            tables[table].push(row); rows = [row];
          }
          if (action === 'update') rows.forEach(row => Object.assign(row, payload));
          return Promise.resolve({ data:structuredClone(single ? rows[0] || null : rows), error:null }).then(resolve);
        },
      };
      return query;
    },
    async rpc(name, args) {
      if (name === 'consume_passkey_challenge') {
        const index = tables.passkey_challenges.findIndex(c => c.id === args.challenge_id);
        return { data:index < 0 ? [] : tables.passkey_challenges.splice(index,1) };
      }
      if (name === 'passkey_rate_limit') {
        const count = (rates.get(args.rate_bucket) || 0) + 1; rates.set(args.rate_bucket, count);
        return { data:count <= args.max_attempts };
      }
      if (name === 'remove_passkey') {
        const index = tables.passkeys.findIndex(p => p.id === args.passkey_id && p.user_id === args.owner_id);
        if (index < 0) return { data:'not_found' };
        const owner = tables.users.find(u => u.user_id === args.owner_id);
        if (!owner?.recovery && tables.passkeys.filter(p => p.user_id === args.owner_id).length === 1) return { data:'last_method' };
        tables.passkeys.splice(index,1); return { data:'removed' };
      }
      throw Error(`Unknown test RPC ${name}`);
    },
  };
}
