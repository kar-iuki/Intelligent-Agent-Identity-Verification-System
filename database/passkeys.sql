-- Apply after schema.sql in the Supabase SQL editor. Service-role access only.
BEGIN;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS webauthn_user_handle uuid NOT NULL DEFAULT gen_random_uuid();
CREATE UNIQUE INDEX IF NOT EXISTS users_webauthn_handle ON public.users(webauthn_user_handle);
CREATE TABLE IF NOT EXISTS public.passkeys (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
  credential_id text NOT NULL UNIQUE,
  public_key text NOT NULL,
  counter bigint NOT NULL DEFAULT 0 CHECK(counter >= 0),
  transports jsonb NOT NULL DEFAULT '[]' CHECK(jsonb_typeof(transports) = 'array'),
  device_type text NOT NULL CHECK(device_type IN ('singleDevice', 'multiDevice')),
  backed_up boolean NOT NULL DEFAULT false,
  label varchar(100) NOT NULL,
  user_agent text, browser text, os text, device_name text,
  created_at timestamptz NOT NULL DEFAULT now(), last_used_at timestamptz
);
CREATE INDEX IF NOT EXISTS passkeys_user_id ON public.passkeys(user_id);
CREATE TABLE IF NOT EXISTS public.passkey_challenges (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  challenge text NOT NULL,
  purpose text NOT NULL CHECK(purpose IN ('login','register')),
  user_id uuid REFERENCES public.users(user_id) ON DELETE CASCADE,
  expires_at timestamptz NOT NULL DEFAULT now() + interval '5 minutes'
);
CREATE TABLE IF NOT EXISTS public.passkey_rate_limits (
  bucket text PRIMARY KEY, attempts integer NOT NULL, expires_at timestamptz NOT NULL
);
ALTER TABLE public.passkeys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.passkey_challenges ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.passkey_rate_limits ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.passkeys, public.passkey_challenges, public.passkey_rate_limits FROM anon, authenticated;
GRANT ALL ON public.passkeys, public.passkey_challenges, public.passkey_rate_limits TO service_role;

-- DELETE RETURNING consumes even expired/mismatched challenges before verification.
CREATE OR REPLACE FUNCTION public.consume_passkey_challenge(challenge_id uuid)
RETURNS SETOF public.passkey_challenges LANGUAGE sql SECURITY DEFINER SET search_path = '' AS $$
  DELETE FROM public.passkey_challenges WHERE id = challenge_id RETURNING *;
$$;
CREATE OR REPLACE FUNCTION public.passkey_rate_limit(rate_bucket text, max_attempts integer)
RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
DECLARE used integer;
BEGIN
  DELETE FROM public.passkey_rate_limits WHERE expires_at < now();
  DELETE FROM public.passkey_challenges WHERE expires_at < now();
  INSERT INTO public.passkey_rate_limits AS r VALUES(rate_bucket, 1, now() + interval '5 minutes')
  ON CONFLICT(bucket) DO UPDATE SET attempts = r.attempts + 1 RETURNING attempts INTO used;
  RETURN used <= max_attempts;
END;
$$;
-- Lock the user to serialize concurrent removals; auth.users is the password source
-- of truth (public.users.password_hash is not used by this application).
CREATE OR REPLACE FUNCTION public.remove_passkey(owner_id uuid, passkey_id uuid)
RETURNS text LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
DECLARE remaining integer; recovery boolean;
BEGIN
  PERFORM 1 FROM public.users WHERE user_id = owner_id FOR UPDATE;
  IF NOT EXISTS(SELECT 1 FROM public.passkeys WHERE id = passkey_id AND user_id = owner_id) THEN RETURN 'not_found'; END IF;
  SELECT count(*) INTO remaining FROM public.passkeys WHERE user_id = owner_id;
  SELECT EXISTS(SELECT 1 FROM auth.users WHERE id = owner_id AND coalesce(encrypted_password, '') <> '')
    OR EXISTS(SELECT 1 FROM auth.identities WHERE user_id = owner_id AND provider <> 'email') INTO recovery;
  IF remaining <= 1 AND NOT recovery THEN RETURN 'last_method'; END IF;
  DELETE FROM public.passkeys WHERE id = passkey_id AND user_id = owner_id;
  RETURN 'removed';
END;
$$;
REVOKE ALL ON FUNCTION public.consume_passkey_challenge(uuid), public.passkey_rate_limit(text,integer), public.remove_passkey(uuid,uuid) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.consume_passkey_challenge(uuid), public.passkey_rate_limit(text,integer), public.remove_passkey(uuid,uuid) TO service_role;
COMMIT;
