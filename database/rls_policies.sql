-- Module 2: Authentication — Row Level Security Policies
-- Run this in the Supabase SQL Editor after schema.sql

-- ============================================================
-- Helper function: check if the current user is an admin
-- ============================================================

CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM users
    WHERE user_id = auth.uid()
    AND role = 'admin'
  );
$$ LANGUAGE sql SECURITY DEFINER STABLE;

-- ============================================================
-- Agents table policies
-- ============================================================

CREATE POLICY "Agents can view own record"
  ON agents FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY "Agents can update own record"
  ON agents FOR UPDATE
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "Admins can view all agents"
  ON agents FOR SELECT
  USING (is_admin());

-- ============================================================
-- Audit Logs table policies
-- ============================================================

CREATE POLICY "Admins can view all audit logs"
  ON audit_logs FOR SELECT
  USING (is_admin());

-- ============================================================
-- Users table policies (needed for role lookups via RLS)
-- ============================================================

CREATE POLICY "Users can view own record"
  ON users FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY "Admins can view all users"
  ON users FOR SELECT
  USING (is_admin());
