-- Contract Management Database Schema
-- PostgreSQL implementation with full-text search

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Contracts table
CREATE TABLE IF NOT EXISTS contracts (
    id SERIAL PRIMARY KEY,
    reference_number VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    contract_type VARCHAR(100),
    status VARCHAR(50) CHECK (status IN ('Draft', 'In Negotiation', 'Executed', 'Active', 'Renewed', 'Expired', 'Terminated')),
    risk_score DECIMAL(5,2) DEFAULT 0.0,
    risk_level VARCHAR(20) CHECK (risk_level IN ('Low', 'Moderate', 'High', 'Critical')),
    
    -- Key dates
    effective_date TIMESTAMP,
    execution_date TIMESTAMP,
    expiration_date TIMESTAMP,
    renewal_date TIMESTAMP,
    
    -- Financial terms
    contract_value DECIMAL(15,2),
    currency VARCHAR(3) DEFAULT 'USD',
    payment_terms VARCHAR(200),
    
    -- Parties
    primary_party_id INTEGER,
    counterparty_id INTEGER,
    
    -- Metadata
    metadata JSONB,
    full_text_search TSVECTOR,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    
    FOREIGN KEY (primary_party_id) REFERENCES parties(id),
    FOREIGN KEY (counterparty_id) REFERENCES parties(id)
);

-- Create index for full-text search
CREATE INDEX idx_contracts_full_text ON contracts USING GIN(full_text_search);
CREATE INDEX idx_contracts_status ON contracts(status);
CREATE INDEX idx_contracts_type ON contracts(contract_type);
CREATE INDEX idx_contracts_risk_level ON contracts(risk_level);
CREATE INDEX idx_contracts_expiration ON contracts(expiration_date);
CREATE INDEX idx_contracts_reference ON contracts(reference_number);

-- Parties table
CREATE TABLE IF NOT EXISTS parties (
    id SERIAL PRIMARY KEY,
    legal_name VARCHAR(500) NOT NULL,
    party_type VARCHAR(50) CHECK (party_type IN ('Vendor', 'Client', 'Internal', 'Partner')),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    contact_email VARCHAR(100),
    contact_phone VARCHAR(20),
    registration_number VARCHAR(100),
    financial_rating VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(legal_name, registration_number)
);

CREATE INDEX idx_parties_name ON parties(legal_name);
CREATE INDEX idx_parties_type ON parties(party_type);

-- Clauses table
CREATE TABLE IF NOT EXISTS clauses (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL,
    clause_type VARCHAR(100),
    title VARCHAR(200),
    content TEXT,
    risk_score DECIMAL(5,2),
    is_standard BOOLEAN DEFAULT true,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
);

CREATE INDEX idx_clauses_contract ON clauses(contract_id);
CREATE INDEX idx_clauses_type ON clauses(clause_type);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL,
    version INTEGER DEFAULT 1,
    filename VARCHAR(500),
    file_path VARCHAR(1000),
    file_size INTEGER,
    file_type VARCHAR(10),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by VARCHAR(100),
    is_executed BOOLEAN DEFAULT false,
    signature_date TIMESTAMP,
    checksum VARCHAR(64),
    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
);

CREATE INDEX idx_documents_contract ON documents(contract_id);
CREATE INDEX idx_documents_uploaded ON documents(uploaded_at);

-- Approvals table
CREATE TABLE IF NOT EXISTS approvals (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL,
    approver_name VARCHAR(100),
    approver_role VARCHAR(100),
    approval_status VARCHAR(20) CHECK (approval_status IN ('Pending', 'Approved', 'Rejected')),
    comments TEXT,
    approved_at TIMESTAMP,
    sequence INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
);

CREATE INDEX idx_approvals_contract ON approvals(contract_id);
CREATE INDEX idx_approvals_status ON approvals(approval_status);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER,
    action VARCHAR(50),
    user_id VARCHAR(100),
    changes JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
);

CREATE INDEX idx_audit_contract ON audit_log(contract_id);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);

-- Function to update full-text search vector
CREATE OR REPLACE FUNCTION update_contract_fts()
RETURNS TRIGGER AS $$
BEGIN
    NEW.full_text_search := to_tsvector('english', COALESCE(NEW.title, '') || ' ' || COALESCE(NEW.description, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update full-text search
CREATE TRIGGER trigger_contract_fts
BEFORE INSERT OR UPDATE ON contracts
FOR EACH ROW
EXECUTE FUNCTION update_contract_fts();

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_contracts_timestamp
BEFORE UPDATE ON contracts
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();
