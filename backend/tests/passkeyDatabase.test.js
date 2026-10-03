import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { PGlite } from '@electric-sql/pglite';

test('PostgreSQL migration enforces replay, privileges, rate limits, uniqueness, scoping and last-method protection', async () => {
  const db = new PGlite();
  try {
    await db.exec(`CREATE ROLE anon; CREATE ROLE authenticated; CREATE ROLE service_role;
      CREATE SCHEMA auth;
      CREATE TABLE auth.users(id uuid PRIMARY KEY, encrypted_password text);
      CREATE TABLE auth.identities(user_id uuid, provider text);
      CREATE TABLE public.users(user_id uuid PRIMARY KEY, email text);
      INSERT INTO public.users VALUES ('11111111-1111-1111-1111-111111111111','one@example.test'), ('22222222-2222-2222-2222-222222222222','two@example.test');
      INSERT INTO auth.users(id) SELECT user_id FROM public.users;`);
    const migration = await readFile(new URL('../../database/passkeys.sql', import.meta.url),'utf8');
    await db.exec(migration);
    await db.exec(migration); // Re-running the migration is safe.
    const one = '11111111-1111-1111-1111-111111111111', two = '22222222-2222-2222-2222-222222222222';
    const handles = (await db.query('SELECT webauthn_user_handle FROM public.users')).rows;
    assert.notEqual(handles[0].webauthn_user_handle,handles[1].webauthn_user_handle);
    const challenge = (await db.query("INSERT INTO public.passkey_challenges(challenge,purpose) VALUES ('random-challenge','login') RETURNING *")).rows[0];
    assert.ok(Date.parse(challenge.expires_at) - Date.now() > 290000);
    assert.equal((await db.query('SELECT * FROM consume_passkey_challenge($1)',[challenge.id])).rows.length,1);
    assert.equal((await db.query('SELECT * FROM consume_passkey_challenge($1)',[challenge.id])).rows.length,0);
    for (let i = 0; i < 3; i++) assert.equal((await db.query("SELECT passkey_rate_limit('ip',2) AS allowed")).rows[0].allowed,i < 2);
    await db.exec("UPDATE passkey_rate_limits SET expires_at = now() - interval '1 second'");
    assert.equal((await db.query("SELECT passkey_rate_limit('ip',2) AS allowed")).rows[0].allowed,true);
    const insert = `INSERT INTO public.passkeys(user_id,credential_id,public_key,device_type,label) VALUES ($1,$2,'AA','multiDevice','Test') RETURNING id`;
    const key = (await db.query(insert,[one,'credential-one'])).rows[0].id;
    await assert.rejects(db.query(insert,[two,'credential-one']));
    const remove = async user => (await db.query('SELECT remove_passkey($1,$2) AS result',[user,key])).rows[0].result;
    assert.equal(await remove(two),'not_found'); assert.equal(await remove(one),'last_method');
    await db.query("UPDATE auth.users SET encrypted_password = 'hash' WHERE id = $1",[one]);
    assert.equal(await remove(one),'removed');
    const googleKey = (await db.query(insert,[two,'credential-two'])).rows[0].id;
    await db.query("INSERT INTO auth.identities VALUES ($1,'google')",[two]);
    assert.equal((await db.query('SELECT remove_passkey($1,$2) AS result',[two,googleKey])).rows[0].result,'removed');
    for (const role of ['anon','authenticated']) {
      const privileges = (await db.query(`SELECT has_table_privilege($1,'public.passkeys','SELECT') AS read,
        has_table_privilege($1,'public.passkey_challenges','INSERT') AS write,
        has_function_privilege($1,'public.remove_passkey(uuid,uuid)','EXECUTE') AS remove`,[role])).rows[0];
      assert.deepEqual(privileges,{ read:false, write:false, remove:false });
    }
    assert.equal((await db.query("SELECT relrowsecurity FROM pg_class WHERE oid = 'public.passkeys'::regclass")).rows[0].relrowsecurity,true);
  } finally { await db.close(); }
});
