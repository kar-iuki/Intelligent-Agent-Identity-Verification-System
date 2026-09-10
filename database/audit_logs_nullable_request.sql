-- Module 3: make audit_logs.request_id nullable so registration
-- actions can be logged before a verification request exists.
-- Run in Supabase SQL Editor.

ALTER TABLE audit_logs
  ALTER COLUMN request_id DROP NOT NULL;
