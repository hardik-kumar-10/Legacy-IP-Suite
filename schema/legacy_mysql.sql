-- Legacy MySQL schema (denormalized, messy data typical of legacy systems)
-- This represents a legacy IPMS with poor data quality and structure

CREATE DATABASE IF NOT EXISTS legacy_ipms;
USE legacy_ipms;

-- Clients table with messy data patterns
CREATE TABLE IF NOT EXISTS clients_legacy (
  client_id VARCHAR(32) PRIMARY KEY,
  client_name VARCHAR(255),
  first_name VARCHAR(255), -- sometimes populated, sometimes not
  last_name VARCHAR(255),  -- sometimes populated, sometimes not
  company_name VARCHAR(255), -- for corporate clients
  client_type ENUM('individual', 'company', 'organization', ''), -- inconsistent
  email VARCHAR(255),
  email_secondary VARCHAR(255),
  phone VARCHAR(64),
  phone_mobile VARCHAR(64),
  fax VARCHAR(64), -- legacy field
  address_line1 VARCHAR(255),
  address_line2 VARCHAR(255),
  city VARCHAR(100),
  state_province VARCHAR(100),
  postal_code VARCHAR(20),
  country VARCHAR(64), -- inconsistent format
  billing_address TEXT, -- sometimes duplicates main address
  created_on VARCHAR(64), -- messy text dates
  modified_on VARCHAR(64),
  status VARCHAR(32), -- active, inactive, suspended
  notes TEXT,
  credit_limit DECIMAL(10,2),
  payment_terms VARCHAR(64)
);

-- Patents table with denormalized structure
CREATE TABLE IF NOT EXISTS patents_legacy (
  patent_id VARCHAR(32) PRIMARY KEY,
  client_id VARCHAR(32),
  title TEXT,
  abstract TEXT,
  inventors TEXT, -- comma-separated names
  assignees TEXT, -- comma-separated names
  application_number VARCHAR(64),
  publication_number VARCHAR(64),
  patent_number VARCHAR(64),
  filing_date VARCHAR(64), -- inconsistent formats
  priority_date VARCHAR(64),
  publication_date VARCHAR(64),
  grant_date VARCHAR(64),
  expiry_date VARCHAR(64),
  jurisdiction VARCHAR(64), -- US, EP, CN, etc.
  patent_office VARCHAR(100),
  status VARCHAR(64), -- pending, granted, abandoned, expired
  patent_type VARCHAR(64), -- utility, design, plant
  technology_field VARCHAR(255),
  ipc_classes TEXT, -- International Patent Classification
  cpc_classes TEXT, -- Cooperative Patent Classification
  family_id VARCHAR(64), -- patent family identifier
  priority_claims TEXT, -- JSON-like string with priority info
  examination_status VARCHAR(100),
  annuity_due_date VARCHAR(64),
  estimated_cost DECIMAL(10,2),
  actual_cost DECIMAL(10,2),
  attorney_ref VARCHAR(100),
  internal_ref VARCHAR(100),
  created_on VARCHAR(64),
  modified_on VARCHAR(64),
  notes TEXT
);

-- Trademarks table
CREATE TABLE IF NOT EXISTS trademarks_legacy (
  tm_id VARCHAR(32) PRIMARY KEY,
  client_id VARCHAR(32),
  mark_text VARCHAR(255),
  mark_type ENUM('word', 'logo', 'combined', 'sound', 'color', ''),
  mark_description TEXT,
  goods_services TEXT, -- description of goods/services
  nice_classes VARCHAR(255), -- comma-separated class numbers
  vienna_classes VARCHAR(255), -- for logo marks
  application_number VARCHAR(64),
  registration_number VARCHAR(64),
  filing_date VARCHAR(64),
  priority_date VARCHAR(64),
  publication_date VARCHAR(64),
  registration_date VARCHAR(64),
  renewal_date VARCHAR(64),
  expiry_date VARCHAR(64),
  jurisdiction VARCHAR(64),
  trademark_office VARCHAR(100),
  status VARCHAR(64), -- pending, registered, opposed, cancelled
  opposition_period_end VARCHAR(64),
  use_basis VARCHAR(100), -- intent-to-use, use-in-commerce
  first_use_date VARCHAR(64),
  first_use_commerce_date VARCHAR(64),
  attorney_ref VARCHAR(100),
  internal_ref VARCHAR(100),
  estimated_cost DECIMAL(10,2),
  actual_cost DECIMAL(10,2),
  created_on VARCHAR(64),
  modified_on VARCHAR(64),
  notes TEXT
);

-- Copyright registrations
CREATE TABLE IF NOT EXISTS copyrights_legacy (
  copyright_id VARCHAR(32) PRIMARY KEY,
  client_id VARCHAR(32),
  work_title VARCHAR(500),
  work_type VARCHAR(100), -- literary, musical, artistic, etc.
  work_description TEXT,
  authors TEXT, -- comma-separated
  copyright_claimants TEXT,
  creation_date VARCHAR(64),
  publication_date VARCHAR(64),
  registration_number VARCHAR(64),
  registration_date VARCHAR(64),
  jurisdiction VARCHAR(64),
  status VARCHAR(64),
  deposit_copies_submitted VARCHAR(10), -- yes/no
  work_made_for_hire VARCHAR(10),
  pseudonymous_work VARCHAR(10),
  derivative_work VARCHAR(10),
  compilation_work VARCHAR(10),
  preexisting_material TEXT,
  new_material TEXT,
  attorney_ref VARCHAR(100),
  internal_ref VARCHAR(100),
  estimated_cost DECIMAL(10,2),
  actual_cost DECIMAL(10,2),
  created_on VARCHAR(64),
  modified_on VARCHAR(64),
  notes TEXT
);

-- Deadlines and renewals
CREATE TABLE IF NOT EXISTS deadlines_legacy (
  deadline_id VARCHAR(32) PRIMARY KEY,
  related_type VARCHAR(32), -- 'patent', 'trademark', 'copyright'
  related_id VARCHAR(32),
  client_id VARCHAR(32),
  deadline_type VARCHAR(100), -- renewal, response, filing, examination
  due_date VARCHAR(64),
  description TEXT,
  priority ENUM('low', 'medium', 'high', 'critical', ''),
  status VARCHAR(32), -- pending, completed, overdue, cancelled
  reminder_sent VARCHAR(10), -- yes/no
  completed_date VARCHAR(64),
  completed_by VARCHAR(100),
  cost DECIMAL(10,2),
  internal_notes TEXT,
  created_on VARCHAR(64),
  modified_on VARCHAR(64)
);

-- Invoices and billing (legacy system)
CREATE TABLE IF NOT EXISTS invoices_legacy (
  invoice_id VARCHAR(32) PRIMARY KEY,
  client_id VARCHAR(32),
  invoice_number VARCHAR(64),
  invoice_date VARCHAR(64),
  due_date VARCHAR(64),
  subtotal DECIMAL(10,2),
  tax_amount DECIMAL(10,2),
  total_amount DECIMAL(10,2),
  currency VARCHAR(10),
  status VARCHAR(32), -- draft, sent, paid, overdue, cancelled
  payment_date VARCHAR(64),
  payment_method VARCHAR(64),
  payment_reference VARCHAR(100),
  billing_address TEXT,
  line_items TEXT, -- JSON-like string with line items
  created_on VARCHAR(64),
  modified_on VARCHAR(64),
  notes TEXT
);

-- Attorney/staff assignments (denormalized)
CREATE TABLE IF NOT EXISTS assignments_legacy (
  assignment_id VARCHAR(32) PRIMARY KEY,
  matter_type VARCHAR(32), -- patent, trademark, copyright
  matter_id VARCHAR(32),
  client_id VARCHAR(32),
  attorney_name VARCHAR(255),
  attorney_email VARCHAR(255),
  attorney_bar_number VARCHAR(100),
  paralegal_name VARCHAR(255),
  role VARCHAR(100), -- lead, associate, paralegal
  assignment_date VARCHAR(64),
  hourly_rate DECIMAL(8,2),
  estimated_hours DECIMAL(8,2),
  actual_hours DECIMAL(8,2),
  status VARCHAR(32),
  created_on VARCHAR(64),
  notes TEXT
);

-- Document management (basic)
CREATE TABLE IF NOT EXISTS documents_legacy (
  document_id VARCHAR(32) PRIMARY KEY,
  related_type VARCHAR(32),
  related_id VARCHAR(32),
  client_id VARCHAR(32),
  document_name VARCHAR(500),
  document_type VARCHAR(100),
  file_path VARCHAR(1000),
  file_size_kb INT,
  mime_type VARCHAR(100),
  upload_date VARCHAR(64),
  uploaded_by VARCHAR(255),
  version VARCHAR(32),
  is_confidential VARCHAR(10),
  expiry_date VARCHAR(64),
  created_on VARCHAR(64),
  notes TEXT
);

-- Seed data for testing
INSERT INTO clients_legacy (client_id, client_name, first_name, last_name, company_name, client_type, email, phone, address_line1, city, state_province, country, created_on, status) VALUES
('CL-001', 'Smith, Mia', 'Mia', 'Smith', NULL, 'individual', 'mia.smith@example.com', '+1-555-0123', '123 Main St', 'New York', 'NY', 'United States', '2021-03-02', 'active'),
('CL-002', 'TechCorp Inc', NULL, NULL, 'TechCorp Inc', 'company', 'legal@techcorp.com', '+1-555-0456', '456 Innovation Dr', 'San Francisco', 'CA', 'USA', '2021-05-15', 'active'),
('CL-003', 'Johnson, Robert', 'Robert', 'Johnson', NULL, '', 'rjohnson@email.com', '555-789-0123', '789 Oak Avenue', 'Austin', 'Texas', 'US', '2022-01-10', 'active')
ON DUPLICATE KEY UPDATE client_name=VALUES(client_name);

INSERT INTO patents_legacy (patent_id, client_id, title, abstract, inventors, filing_date, grant_date, jurisdiction, status, patent_type, technology_field, created_on) VALUES
('PT-0001', 'CL-001', 'Method for Efficient Data Processing', 'A novel method for processing large datasets using machine learning algorithms...', 'Smith, Mia; Johnson, David', '03/02/2021', '2022-08-10', 'US', 'granted', 'utility', 'Computer Science', '2021-03-02'),
('PT-0002', 'CL-002', 'Wireless Communication Device', 'An improved wireless device with enhanced signal processing capabilities...', 'Chen, Li; Patel, Raj', '2021-07-20', '', 'US', 'pending', 'utility', 'Telecommunications', '2021-07-20'),
('PT-0003', 'CL-003', 'Biodegradable Packaging Material', 'A sustainable packaging material made from renewable resources...', 'Johnson, Robert', '2022-03-15', '', 'EP', 'pending', 'utility', 'Materials Science', '2022-03-15')
ON DUPLICATE KEY UPDATE title=VALUES(title);

INSERT INTO trademarks_legacy (tm_id, client_id, mark_text, mark_type, nice_classes, filing_date, status, jurisdiction, created_on) VALUES
('TM-0001', 'CL-001', 'INNOVATECH', 'word', '9,42', '2021-05-15', 'registered', 'US', '2021-05-15'),
('TM-0002', 'CL-002', 'TECHCORP LOGO', 'logo', '35,42', '2021-08-01', 'pending', 'US', '2021-08-01'),
('TM-0003', 'CL-003', 'ECOPACK', 'word', '16,39', '2022-04-01', 'pending', 'EU', '2022-04-01')
ON DUPLICATE KEY UPDATE mark_text=VALUES(mark_text);

INSERT INTO deadlines_legacy (deadline_id, related_type, related_id, client_id, deadline_type, due_date, description, priority, status, created_on) VALUES
('DL-0001', 'patent', 'PT-0001', 'CL-001', 'renewal', '2025-11-01', 'Patent renewal fee due', 'high', 'pending', '2021-03-02'),
('DL-0002', 'trademark', 'TM-0001', 'CL-001', 'renewal', '2026-05-15', 'Trademark renewal due', 'medium', 'pending', '2021-05-15'),
('DL-0003', 'patent', 'PT-0002', 'CL-002', 'examination', '2024-01-20', 'Respond to office action', 'critical', 'pending', '2023-10-20')
ON DUPLICATE KEY UPDATE description=VALUES(description);
