-- Add date of birth to agents (used for OCR matching against ID / passport)
ALTER TABLE agents
  ADD COLUMN IF NOT EXISTS date_of_birth DATE;

COMMENT ON COLUMN agents.date_of_birth IS 'Agent date of birth; matched against OCR from identity documents';
