-- Module 8: add decision_basis to KYC decisions for placeholder vs SVM tracking
-- Run in Supabase SQL Editor

ALTER TABLE kyc_decisions
  ADD COLUMN IF NOT EXISTS decision_basis VARCHAR(100) NOT NULL DEFAULT 'placeholder_threshold';

-- Optional metadata for fraud guardrails (IP / device fingerprint)
ALTER TABLE audit_logs
  ADD COLUMN IF NOT EXISTS ip_address VARCHAR(100),
  ADD COLUMN IF NOT EXISTS device_fingerprint VARCHAR(255);

CREATE INDEX IF NOT EXISTS idx_audit_logs_ip_timestamp
  ON audit_logs(ip_address, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_audit_logs_fingerprint_timestamp
  ON audit_logs(device_fingerprint, timestamp DESC);
