-- Intelligent Agent Identity Verification System
-- Run this script in the Supabase SQL Editor (Dashboard > SQL Editor > New query)

-- ============================================================
-- Custom ENUM types
-- ============================================================

CREATE TYPE user_role AS ENUM ('agent', 'admin');

CREATE TYPE verification_status AS ENUM ('pending', 'verified', 'review', 'rejected');

CREATE TYPE kyc_decision AS ENUM ('verified', 'review', 'rejected');

-- ============================================================
-- Users
-- ============================================================

CREATE TABLE users (
    user_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    role          user_role NOT NULL DEFAULT 'agent',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- Agents
-- ============================================================

CREATE TABLE agents (
    agent_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
    full_name         VARCHAR(255) NOT NULL,
    phone_number      VARCHAR(50),
    national_id       VARCHAR(100) NOT NULL UNIQUE,
    profile_photo_url TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- Documents
-- ============================================================

CREATE TABLE documents (
    document_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id      UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    document_type VARCHAR(100) NOT NULL,
    file_url      TEXT NOT NULL,
    uploaded_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- Verification Requests
-- ============================================================

CREATE TABLE verification_requests (
    request_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id    UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    status      verification_status NOT NULL DEFAULT 'pending',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- Verification Scores
-- ============================================================

CREATE TABLE verification_scores (
    score_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id            UUID NOT NULL UNIQUE REFERENCES verification_requests(request_id) ON DELETE CASCADE,
    face_match_score      FLOAT NOT NULL,
    liveness_score        FLOAT NOT NULL,
    ocr_confidence_score  FLOAT NOT NULL,
    blur_score            FLOAT NOT NULL,
    brightness_score      FLOAT NOT NULL,
    contrast_score        FLOAT NOT NULL
);

-- ============================================================
-- KYC Decisions
-- ============================================================

CREATE TABLE kyc_decisions (
    decision_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id           UUID NOT NULL UNIQUE REFERENCES verification_requests(request_id) ON DELETE CASCADE,
    final_decision       kyc_decision NOT NULL,
    verified_probability FLOAT NOT NULL,
    review_probability   FLOAT NOT NULL,
    rejected_probability FLOAT NOT NULL,
    decided_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- Access Control Records
-- ============================================================

CREATE TABLE access_control_records (
    record_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id       UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    decision_id    UUID NOT NULL UNIQUE REFERENCES kyc_decisions(decision_id) ON DELETE CASCADE,
    access_granted BOOLEAN NOT NULL DEFAULT FALSE,
    enforced_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- Audit Logs
-- ============================================================

CREATE TABLE audit_logs (
    log_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id   UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    request_id UUID REFERENCES verification_requests(request_id) ON DELETE CASCADE,
    action     VARCHAR(255) NOT NULL,
    outcome    VARCHAR(255) NOT NULL,
    timestamp  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- Indexes for common query patterns
-- ============================================================

CREATE INDEX idx_agents_user_id ON agents(user_id);
CREATE INDEX idx_documents_agent_id ON documents(agent_id);
CREATE INDEX idx_verification_requests_agent_id ON verification_requests(agent_id);
CREATE INDEX idx_verification_requests_status ON verification_requests(status);
CREATE INDEX idx_audit_logs_agent_id ON audit_logs(agent_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);

-- ============================================================
-- Row Level Security (RLS) — enable on all tables
-- Policies will be added in a later module when auth is wired up
-- ============================================================

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE verification_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE verification_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE kyc_decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE access_control_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
