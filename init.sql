-- ===========================================
-- TanıAI Database Initialization Script
-- ===========================================

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS taniai_db;

-- Use the database
\c taniai_db;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS radiology;
CREATE SCHEMA IF NOT EXISTS diagnosis;
CREATE SCHEMA IF NOT EXISTS medication;
CREATE SCHEMA IF NOT EXISTS appointment;
CREATE SCHEMA IF NOT EXISTS triage;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE taniai_db TO taniai_user;
GRANT ALL PRIVILEGES ON SCHEMA radiology TO taniai_user;
GRANT ALL PRIVILEGES ON SCHEMA diagnosis TO taniai_user;
GRANT ALL PRIVILEGES ON SCHEMA medication TO taniai_user;
GRANT ALL PRIVILEGES ON SCHEMA appointment TO taniai_user;
GRANT ALL PRIVILEGES ON SCHEMA triage TO taniai_user;

-- Create basic tables for each module
-- Radiology module tables
CREATE TABLE IF NOT EXISTS radiology.analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    image_type VARCHAR(50) NOT NULL,
    analysis_type VARCHAR(50) NOT NULL,
    result_data JSONB NOT NULL,
    confidence_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Diagnosis module tables
CREATE TABLE IF NOT EXISTS diagnosis.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    age INTEGER,
    gender VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS diagnosis.diagnosis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES diagnosis.users(id),
    symptoms JSONB NOT NULL,
    diagnosis_result JSONB NOT NULL,
    confidence_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Medication module tables
CREATE TABLE IF NOT EXISTS medication.medications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    medication_name VARCHAR(255) NOT NULL,
    dosage VARCHAR(100),
    frequency VARCHAR(100),
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Appointment module tables
CREATE TABLE IF NOT EXISTS appointment.appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    clinic_name VARCHAR(255) NOT NULL,
    appointment_date TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(50) DEFAULT 'scheduled',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Triage module tables
CREATE TABLE IF NOT EXISTS triage.triage_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symptoms TEXT NOT NULL,
    triage_result JSONB NOT NULL,
    urgency_level VARCHAR(50),
    recommended_clinic VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_analysis_results_image_type ON radiology.analysis_results(image_type);
CREATE INDEX IF NOT EXISTS idx_analysis_results_created_at ON radiology.analysis_results(created_at);
CREATE INDEX IF NOT EXISTS idx_diagnosis_results_user_id ON diagnosis.diagnosis_results(user_id);
CREATE INDEX IF NOT EXISTS idx_diagnosis_results_created_at ON diagnosis.diagnosis_results(created_at);
CREATE INDEX IF NOT EXISTS idx_medications_user_id ON medication.medications(user_id);
CREATE INDEX IF NOT EXISTS idx_appointments_user_id ON appointment.appointments(user_id);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointment.appointments(appointment_date);
CREATE INDEX IF NOT EXISTS idx_triage_results_created_at ON triage.triage_results(created_at);

-- Insert sample data
INSERT INTO diagnosis.users (email, name, age, gender) VALUES 
('test@example.com', 'Test User', 30, 'male'),
('demo@example.com', 'Demo User', 25, 'female')
ON CONFLICT (email) DO NOTHING;

-- Create functions for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_analysis_results_updated_at BEFORE UPDATE ON radiology.analysis_results FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON diagnosis.users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_medications_updated_at BEFORE UPDATE ON medication.medications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_appointments_updated_at BEFORE UPDATE ON appointment.appointments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
