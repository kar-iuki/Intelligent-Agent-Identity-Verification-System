-- Apply in Supabase before deploying the updated backend.
BEGIN;
ALTER TABLE public.verification_requests ADD COLUMN IF NOT EXISTS admin_reviewed_at timestamptz;

-- Earlier releases rewrote the classifier row. Recover only from the original
-- system event for this request and decision, never from the admin's outcome.
WITH previous_reviews AS (
  SELECT DISTINCT ON (r.request_id) r.request_id, l.timestamp AS reviewed_at
  FROM public.verification_requests r
  JOIN public.audit_logs l USING (request_id, agent_id)
  WHERE r.admin_reviewed_at IS NULL AND
    ((l.action = 'ADMIN_APPROVED' AND r.status = 'verified') OR
     (l.action = 'ADMIN_REJECTED' AND r.status = 'rejected'))
  ORDER BY r.request_id, l.timestamp DESC, l.log_id DESC
), tagged AS (
  UPDATE public.verification_requests r SET admin_reviewed_at = a.reviewed_at
  FROM previous_reviews a WHERE r.request_id = a.request_id
  RETURNING r.request_id, r.status, r.admin_reviewed_at
), originals AS (
  SELECT d.decision_id, l.details, l.timestamp
  FROM tagged t JOIN public.kyc_decisions d USING (request_id)
  LEFT JOIN LATERAL (
    SELECT log.details, log.timestamp FROM public.audit_logs log
    WHERE log.request_id = t.request_id AND log.action = 'KYC_DECISION_MADE'
      AND log.performed_by = 'system' AND log.timestamp <= t.admin_reviewed_at
      AND log.details->>'decisionId' = d.decision_id::text
      AND log.details->>'decision' IN ('review', 'verified', 'rejected')
      AND log.details->>'decisionBasis' IN ('svm_model', 'placeholder_threshold')
      AND jsonb_typeof(log.details->'verifiedProbability') = 'number'
      AND jsonb_typeof(log.details->'reviewProbability') = 'number'
      AND jsonb_typeof(log.details->'rejectedProbability') = 'number'
    ORDER BY log.timestamp DESC LIMIT 1
  ) l ON true
  WHERE d.final_decision::text = t.status::text
)
UPDATE public.kyc_decisions d SET
  final_decision = COALESCE((o.details->>'decision')::public.kyc_decision, d.final_decision),
  verified_probability = COALESCE((o.details->>'verifiedProbability')::float, d.verified_probability),
  review_probability = COALESCE((o.details->>'reviewProbability')::float, d.review_probability),
  rejected_probability = COALESCE((o.details->>'rejectedProbability')::float, d.rejected_probability),
  decided_at = COALESCE(o.timestamp, d.decided_at),
  decision_basis = COALESCE(o.details->>'decisionBasis', 'legacy_admin_override')
FROM originals o WHERE o.decision_id = d.decision_id;

CREATE OR REPLACE FUNCTION public.resolve_manual_review(
  p_agent_id uuid, p_request_id uuid, p_reviewer uuid, p_status public.verification_status,
  p_reason text, p_ip text
) RETURNS jsonb LANGUAGE plpgsql SECURITY INVOKER SET search_path = public AS $$
DECLARE
  r verification_requests%ROWTYPE;
  d kyc_decisions%ROWTYPE;
  a access_control_records%ROWTYPE;
  approved boolean := p_status = 'verified';
  review_time timestamptz := now();
BEGIN
  IF p_status IS NULL OR p_status NOT IN ('verified', 'rejected') THEN
    RAISE EXCEPTION 'Invalid review outcome';
  END IF;
  SELECT * INTO r FROM verification_requests WHERE request_id = p_request_id AND agent_id = p_agent_id FOR UPDATE;
  IF NOT FOUND THEN RETURN jsonb_build_object('error', 'Request not found', 'status', 404); END IF;
  SELECT * INTO d FROM kyc_decisions WHERE request_id = p_request_id;
  IF NOT FOUND THEN RETURN jsonb_build_object('error', 'No automated decision yet', 'status', 409); END IF;
  IF r.admin_reviewed_at IS NOT NULL AND r.status = p_status THEN
    SELECT * INTO a FROM access_control_records WHERE decision_id = d.decision_id;
  ELSE
    IF r.status <> 'review' OR r.admin_reviewed_at IS NOT NULL OR d.final_decision <> 'review' THEN
      RETURN jsonb_build_object('error', 'Case is no longer awaiting manual review', 'status', 409);
    END IF;
    -- OCR can provisionally flag a request before the automated access write finishes.
    IF NOT EXISTS (SELECT 1 FROM access_control_records WHERE decision_id = d.decision_id)
       AND NOT EXISTS (SELECT 1 FROM audit_logs WHERE request_id = p_request_id AND action = 'KYC_DECISION_MADE' AND performed_by = 'system' AND details->>'decision' = 'review') THEN
      RETURN jsonb_build_object('error', 'Automated decision is still being recorded', 'status', 409);
    END IF;
    UPDATE verification_requests SET status = p_status, admin_reviewed_at = review_time
      WHERE request_id = p_request_id RETURNING * INTO r;
    INSERT INTO access_control_records(agent_id, decision_id, access_granted, enforced_at)
      VALUES (p_agent_id, d.decision_id, approved, review_time)
      ON CONFLICT (decision_id) DO UPDATE SET access_granted = EXCLUDED.access_granted, enforced_at = EXCLUDED.enforced_at
      RETURNING * INTO a;
    INSERT INTO audit_logs(agent_id, request_id, performed_by, ip_address, action, outcome, details)
      VALUES (p_agent_id, p_request_id, p_reviewer::text, p_ip,
        CASE WHEN approved THEN 'ADMIN_APPROVED' ELSE 'ADMIN_REJECTED' END,
        upper(p_status::text), jsonb_build_object('accessGranted', approved, 'reason', p_reason)),
      (p_agent_id, p_request_id, p_reviewer::text, p_ip,
        CASE WHEN approved THEN 'ACCESS_GRANTED' ELSE 'ACCESS_DENIED' END,
        CASE WHEN approved THEN 'SUCCESS' ELSE 'REJECTED' END,
        jsonb_build_object('source', CASE WHEN approved THEN 'admin_approval' ELSE 'admin_rejection' END, 'reason', p_reason));
  END IF;
  RETURN jsonb_build_object('request', to_jsonb(r), 'decision', to_jsonb(d), 'access', to_jsonb(a));
END;
$$;
REVOKE ALL ON FUNCTION public.resolve_manual_review(uuid,uuid,uuid,public.verification_status,text,text) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.resolve_manual_review(uuid,uuid,uuid,public.verification_status,text,text) TO service_role;
COMMIT;
