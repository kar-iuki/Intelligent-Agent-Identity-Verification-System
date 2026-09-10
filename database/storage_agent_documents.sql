-- Module 3: Supabase Storage bucket + policies for agent-documents
-- Run in Supabase SQL Editor after creating the bucket (or create via dashboard).
--
-- Dashboard alternative:
--   Storage → New bucket → name: agent-documents → Private
--
-- Then run the policies below.

INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'agent-documents',
  'agent-documents',
  false,
  5242880,
  ARRAY['image/jpeg', 'image/png']
)
ON CONFLICT (id) DO UPDATE SET
  public = false,
  file_size_limit = 5242880,
  allowed_mime_types = ARRAY['image/jpeg', 'image/png'];

-- Agents can upload / update / read only inside their own agent folder
CREATE POLICY "Agents can upload own documents"
ON storage.objects FOR INSERT TO authenticated
WITH CHECK (
  bucket_id = 'agent-documents'
  AND (storage.foldername(name))[1] IN (
    SELECT agent_id::text FROM agents WHERE user_id = auth.uid()
  )
);

CREATE POLICY "Agents can update own documents"
ON storage.objects FOR UPDATE TO authenticated
USING (
  bucket_id = 'agent-documents'
  AND (storage.foldername(name))[1] IN (
    SELECT agent_id::text FROM agents WHERE user_id = auth.uid()
  )
);

CREATE POLICY "Agents can read own documents"
ON storage.objects FOR SELECT TO authenticated
USING (
  bucket_id = 'agent-documents'
  AND (storage.foldername(name))[1] IN (
    SELECT agent_id::text FROM agents WHERE user_id = auth.uid()
  )
);

CREATE POLICY "Admins can read all agent documents"
ON storage.objects FOR SELECT TO authenticated
USING (
  bucket_id = 'agent-documents'
  AND is_admin()
);
