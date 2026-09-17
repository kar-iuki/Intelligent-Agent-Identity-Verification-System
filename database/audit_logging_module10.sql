-- Module 10: Audit Logging Consolidation
-- Run in Supabase SQL Editor

-- Extra context columns (snake_case to match existing schema)
ALTER TABLE audit_logs
  ADD COLUMN IF NOT EXISTS details JSONB;

ALTER TABLE audit_logs
  ADD COLUMN IF NOT EXISTS performed_by TEXT;

-- Ensure IP column exists (added in Module 8; widen if needed)
ALTER TABLE audit_logs
  ADD COLUMN IF NOT EXISTS ip_address VARCHAR(45);

-- Auth events (login/logout) may not have an agent yet
ALTER TABLE audit_logs
  ALTER COLUMN agent_id DROP NOT NULL;

-- ============================================================
-- RLS: Audit logs are immutable; inserts via service role only
-- ============================================================

ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Admins can view all audit logs" ON audit_logs;
DROP POLICY IF EXISTS "Agents can view own audit logs" ON audit_logs;
DROP POLICY IF EXISTS "No updates on audit logs" ON audit_logs;
DROP POLICY IF EXISTS "No deletes on audit logs" ON audit_logs;
DROP POLICY IF EXISTS "Service role inserts audit logs" ON audit_logs;

CREATE POLICY "Admins can view all audit logs"
  ON audit_logs FOR SELECT
  USING (is_admin());

CREATE POLICY "Agents can view own audit logs"
  ON audit_logs FOR SELECT
  USING (
    agent_id IN (
      SELECT agent_id FROM agents WHERE user_id = auth.uid()
    )
  );

-- Block authenticated clients from mutating logs (service role bypasses RLS)
CREATE POLICY "No updates on audit logs"
  ON audit_logs FOR UPDATE
  USING (false);

CREATE POLICY "No deletes on audit logs"
  ON audit_logs FOR DELETE
  USING (false);

-- No INSERT policy for authenticated/anon roles — only service role can insert
