-- Modern PostgreSQL IPMS Schema
-- Properly normalized with referential integrity and modern data types

-- Enable UUID extension for better primary keys
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Countries reference table
CREATE TABLE countries (
    id SERIAL PRIMARY KEY,
    iso_code VARCHAR(2) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert common countries
INSERT INTO countries (iso_code, name) VALUES 
('US', 'United States'),
('CA', 'Canada'),
('GB', 'United Kingdom'),
('DE', 'Germany'),
('FR', 'France'),
('JP', 'Japan'),
('CN', 'China'),
('IN', 'India'),
('AU', 'Australia'),
('BR', 'Brazil')
ON CONFLICT (iso_code) DO NOTHING;

-- Jurisdictions for IP filings
CREATE TABLE jurisdictions (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    country_id INTEGER REFERENCES countries(id),
    patent_office VARCHAR(200),
    trademark_office VARCHAR(200),
    copyright_office VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert major jurisdictions
INSERT INTO jurisdictions (code, name, country_id, patent_office, trademark_office) VALUES 
('US', 'United States', 1, 'USPTO', 'USPTO'),
('EP', 'European Patent Office', NULL, 'EPO', NULL),
('GB', 'United Kingdom', 3, 'UKIPO', 'UKIPO'),
('DE', 'Germany', 4, 'DPMA', 'DPMA'),
('JP', 'Japan', 6, 'JPO', 'JPO'),
('CN', 'China', 7, 'CNIPA', 'CNIPA'),
('WIPO', 'World Intellectual Property Organization', NULL, 'WIPO', 'WIPO')
ON CONFLICT (code) DO NOTHING;

-- Clients table (normalized)
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    external_ref VARCHAR(50) UNIQUE, -- for migration tracking
    client_type VARCHAR(20) NOT NULL CHECK (client_type IN ('individual', 'company', 'organization')),
    
    -- Individual client fields
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    
    -- Company client fields  
    company_name VARCHAR(255),
    
    -- Contact information
    email VARCHAR(255) UNIQUE,
    email_secondary VARCHAR(255),
    phone VARCHAR(50),
    phone_mobile VARCHAR(50),
    
    -- Address
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state_province VARCHAR(100),
    postal_code VARCHAR(20),
    country_id INTEGER REFERENCES countries(id),
    
    -- Business fields
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    credit_limit DECIMAL(12,2),
    payment_terms INTEGER, -- days
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT,
    
    -- Constraints
    CONSTRAINT chk_client_name CHECK (
        (client_type = 'individual' AND first_name IS NOT NULL AND last_name IS NOT NULL) OR
        (client_type IN ('company', 'organization') AND company_name IS NOT NULL)
    )
);

-- Attorneys/Staff table
CREATE TABLE attorneys (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    bar_number VARCHAR(100),
    bar_state VARCHAR(10),
    specialization TEXT[],
    hourly_rate DECIMAL(8,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Patents table (normalized)
CREATE TABLE patents (
    id SERIAL PRIMARY KEY,
    external_ref VARCHAR(50) UNIQUE,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    
    -- Patent identification
    application_number VARCHAR(100),
    publication_number VARCHAR(100),
    patent_number VARCHAR(100),
    
    -- Content
    title TEXT NOT NULL,
    abstract TEXT,
    
    -- Important dates
    filing_date DATE,
    priority_date DATE,
    publication_date DATE,
    grant_date DATE,
    expiry_date DATE,
    
    -- Status and type
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'granted', 'abandoned', 'expired', 'rejected')),
    patent_type VARCHAR(20) DEFAULT 'utility' CHECK (patent_type IN ('utility', 'design', 'plant')),
    examination_status VARCHAR(50),
    
    -- Classifications (stored as arrays)
    ipc_classes TEXT[],
    cpc_classes TEXT[],
    
    -- Cost tracking
    estimated_cost DECIMAL(10,2),
    actual_cost DECIMAL(10,2),
    
    -- References
    attorney_ref VARCHAR(100),
    internal_ref VARCHAR(100),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT
);

-- Patent inventors (normalized many-to-many)
CREATE TABLE patent_inventors (
    id SERIAL PRIMARY KEY,
    patent_id INTEGER NOT NULL REFERENCES patents(id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    address TEXT,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Nice classification for trademarks
CREATE TABLE nice_classifications (
    class_number INTEGER PRIMARY KEY CHECK (class_number BETWEEN 1 AND 45),
    description TEXT NOT NULL,
    category VARCHAR(20) CHECK (category IN ('goods', 'services'))
);

-- Insert Nice classifications (abbreviated)
INSERT INTO nice_classifications (class_number, description, category) VALUES
(1, 'Chemicals used in industry, science and photography', 'goods'),
(9, 'Scientific, nautical, surveying, photographic, cinematographic, optical apparatus', 'goods'),
(16, 'Paper, cardboard and goods made from these materials', 'goods'),
(35, 'Advertising; business management; business administration', 'services'),
(42, 'Scientific and technological services and research and design', 'services')
ON CONFLICT (class_number) DO NOTHING;

-- Trademarks table (normalized)
CREATE TABLE trademarks (
    id SERIAL PRIMARY KEY,
    external_ref VARCHAR(50) UNIQUE,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    
    -- Mark details
    mark_text VARCHAR(500),
    mark_type VARCHAR(20) DEFAULT 'word' CHECK (mark_type IN ('word', 'logo', 'combined', 'sound', 'color', 'motion')),
    mark_description TEXT,
    
    -- Application details
    application_number VARCHAR(100),
    registration_number VARCHAR(100),
    
    -- Goods and services
    goods_services TEXT,
    
    -- Important dates
    filing_date DATE,
    priority_date DATE,
    publication_date DATE,
    registration_date DATE,
    renewal_date DATE,
    expiry_date DATE,
    
    -- Use basis (US specific)
    use_basis VARCHAR(50),
    first_use_date DATE,
    first_use_commerce_date DATE,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'registered', 'opposed', 'cancelled', 'expired', 'abandoned')),
    
    -- Cost tracking
    estimated_cost DECIMAL(10,2),
    actual_cost DECIMAL(10,2),
    
    -- References
    attorney_ref VARCHAR(100),
    internal_ref VARCHAR(100),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT
);

-- Trademark Nice classifications (many-to-many)
CREATE TABLE trademark_nice_classes (
    id SERIAL PRIMARY KEY,
    trademark_id INTEGER NOT NULL REFERENCES trademarks(id) ON DELETE CASCADE,
    nice_class_id INTEGER NOT NULL REFERENCES nice_classifications(class_number),
    goods_services_description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(trademark_id, nice_class_id)
);

-- Copyrights table
CREATE TABLE copyrights (
    id SERIAL PRIMARY KEY,
    external_ref VARCHAR(50) UNIQUE,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    
    -- Work details
    work_title VARCHAR(500) NOT NULL,
    work_type VARCHAR(100), -- literary, musical, artistic, dramatic, etc.
    work_description TEXT,
    
    -- Registration details
    registration_number VARCHAR(100),
    registration_date DATE,
    
    -- Important dates
    creation_date DATE,
    publication_date DATE,
    
    -- Work characteristics
    work_made_for_hire BOOLEAN DEFAULT FALSE,
    pseudonymous_work BOOLEAN DEFAULT FALSE,
    derivative_work BOOLEAN DEFAULT FALSE,
    compilation_work BOOLEAN DEFAULT FALSE,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'registered', 'rejected', 'abandoned')),
    
    -- Cost tracking
    estimated_cost DECIMAL(10,2),
    actual_cost DECIMAL(10,2),
    
    -- References
    attorney_ref VARCHAR(100),
    internal_ref VARCHAR(100),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT
);

-- Deadlines and renewals (normalized)
CREATE TABLE deadlines (
    id SERIAL PRIMARY KEY,
    external_ref VARCHAR(50) UNIQUE,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    
    -- Related IP matter (polymorphic relationship)
    related_table VARCHAR(20) CHECK (related_table IN ('patents', 'trademarks', 'copyrights')),
    related_id INTEGER NOT NULL,
    
    -- Deadline details
    deadline_type VARCHAR(100) NOT NULL, -- renewal, response, filing, examination, etc.
    due_date DATE NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    
    -- Status tracking
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'overdue', 'cancelled')),
    completed_date DATE,
    
    -- Cost
    estimated_cost DECIMAL(10,2),
    actual_cost DECIMAL(10,2),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    internal_notes TEXT
);

-- Invoices
CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id),
    
    -- Invoice details
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    invoice_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    
    -- Amounts
    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0,
    tax_rate DECIMAL(5,4) DEFAULT 0,
    tax_amount DECIMAL(12,2) DEFAULT 0,
    total_amount DECIMAL(12,2) DEFAULT 0,
    
    -- Currency and payment
    currency VARCHAR(3) DEFAULT 'USD',
    payment_terms INTEGER DEFAULT 30, -- days
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'sent', 'paid', 'overdue', 'cancelled')),
    
    -- Payment tracking
    payment_date DATE,
    payment_method VARCHAR(50),
    payment_reference VARCHAR(100),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT
);

-- Documents management
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    external_ref VARCHAR(50) UNIQUE,
    
    -- Related matter (polymorphic)
    related_table VARCHAR(20) CHECK (related_table IN ('clients', 'patents', 'trademarks', 'copyrights')),
    related_id INTEGER NOT NULL,
    
    -- Document details
    document_name VARCHAR(500) NOT NULL,
    document_type VARCHAR(100), -- application, response, certificate, etc.
    file_path VARCHAR(1000),
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    
    -- Security
    is_confidential BOOLEAN DEFAULT FALSE,
    
    -- Versioning
    version VARCHAR(20) DEFAULT '1.0',
    
    -- Lifecycle
    upload_date TIMESTAMPTZ DEFAULT NOW(),
    expiry_date DATE,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT
);

-- Audit tables for migration tracking
CREATE TABLE migration_runs (
    id BIGSERIAL PRIMARY KEY,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'running' CHECK (status IN ('running', 'success', 'failed')),
    total_records_processed INTEGER DEFAULT 0,
    errors_encountered INTEGER DEFAULT 0,
    notes TEXT
);

CREATE TABLE migration_row_counts (
    run_id BIGINT REFERENCES migration_runs(id) ON DELETE CASCADE,
    table_name VARCHAR(100),
    inserted INTEGER DEFAULT 0,
    updated INTEGER DEFAULT 0,
    failed INTEGER DEFAULT 0,
    CONSTRAINT pk_migration_row_counts PRIMARY KEY (run_id, table_name)
);

-- Create indexes for performance
CREATE INDEX idx_clients_email ON clients(email);
CREATE INDEX idx_clients_external_ref ON clients(external_ref);
CREATE INDEX idx_clients_status ON clients(status);

CREATE INDEX idx_patents_client_id ON patents(client_id);
CREATE INDEX idx_patents_status ON patents(status);
CREATE INDEX idx_patents_filing_date ON patents(filing_date);
CREATE INDEX idx_patents_external_ref ON patents(external_ref);

CREATE INDEX idx_trademarks_client_id ON trademarks(client_id);
CREATE INDEX idx_trademarks_status ON trademarks(status);
CREATE INDEX idx_trademarks_filing_date ON trademarks(filing_date);
CREATE INDEX idx_trademarks_external_ref ON trademarks(external_ref);

CREATE INDEX idx_copyrights_client_id ON copyrights(client_id);
CREATE INDEX idx_copyrights_external_ref ON copyrights(external_ref);

CREATE INDEX idx_deadlines_due_date ON deadlines(due_date);
CREATE INDEX idx_deadlines_status ON deadlines(status);
CREATE INDEX idx_deadlines_client_id ON deadlines(client_id);
CREATE INDEX idx_deadlines_related ON deadlines(related_table, related_id);

-- Create functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_patents_updated_at BEFORE UPDATE ON patents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_trademarks_updated_at BEFORE UPDATE ON trademarks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_copyrights_updated_at BEFORE UPDATE ON copyrights FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_deadlines_updated_at BEFORE UPDATE ON deadlines FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON invoices FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
