-- Job System Database Schema
-- Run this in your Supabase SQL editor

-- 1. Add company role to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('admin', 'user', 'company'));

-- 2. Create companies table
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    website VARCHAR(255),
    industry VARCHAR(100),
    size VARCHAR(50),
    location VARCHAR(255),
    created_by INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Create jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT,
    location VARCHAR(255),
    salary_min INTEGER,
    salary_max INTEGER,
    employment_type VARCHAR(50) CHECK (employment_type IN ('full-time', 'part-time', 'contract', 'internship', 'freelance')),
    experience_level VARCHAR(50) CHECK (experience_level IN ('entry', 'mid', 'senior', 'executive')),
    remote_work BOOLEAN DEFAULT FALSE,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    posted_by INTEGER REFERENCES users(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    application_deadline DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Create job applications table
CREATE TABLE IF NOT EXISTS job_applications (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    applicant_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    cover_letter TEXT,
    resume_url VARCHAR(500),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'reviewed', 'accepted', 'rejected')),
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    notes TEXT
);

-- 5. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_companies_created_by ON companies(created_by);
CREATE INDEX IF NOT EXISTS idx_jobs_company_id ON jobs(company_id);
CREATE INDEX IF NOT EXISTS idx_jobs_posted_by ON jobs(posted_by);
CREATE INDEX IF NOT EXISTS idx_jobs_is_active ON jobs(is_active);
CREATE INDEX IF NOT EXISTS idx_jobs_employment_type ON jobs(employment_type);
CREATE INDEX IF NOT EXISTS idx_jobs_experience_level ON jobs(experience_level);
CREATE INDEX IF NOT EXISTS idx_job_applications_job_id ON job_applications(job_id);
CREATE INDEX IF NOT EXISTS idx_job_applications_applicant_id ON job_applications(applicant_id);
CREATE INDEX IF NOT EXISTS idx_job_applications_status ON job_applications(status);

-- 6. Create function to automatically update updated_at timestamp for companies
CREATE OR REPLACE FUNCTION update_companies_updated_at_column() RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 7. Create function to automatically update updated_at timestamp for jobs
CREATE OR REPLACE FUNCTION update_jobs_updated_at_column() RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 8. Create triggers to automatically update updated_at
DROP TRIGGER IF EXISTS update_companies_updated_at ON companies;
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies FOR EACH ROW EXECUTE FUNCTION update_companies_updated_at_column();

DROP TRIGGER IF EXISTS update_jobs_updated_at ON jobs;
CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs FOR EACH ROW EXECUTE FUNCTION update_jobs_updated_at_column();

-- 9. Insert sample company (optional - for testing)
INSERT INTO companies (name, description, website, industry, size, location, created_by) 
VALUES (
    'TechCorp Solutions', 
    'Leading technology company specializing in software development and digital solutions.',
    'https://techcorp.com',
    'Technology',
    '50-200',
    'San Francisco, CA',
    1
) ON CONFLICT DO NOTHING;

-- 10. Update existing users to have default role (if not already set)
UPDATE users SET role = 'user' WHERE role IS NULL;

-- 11. Set one user as company role (you can change the email as needed)
UPDATE users SET role = 'company' WHERE email = 'company@example.com';

-- 12. Insert sample jobs (optional - for testing)
INSERT INTO jobs (title, description, requirements, location, salary_min, salary_max, employment_type, experience_level, remote_work, company_id, posted_by) 
VALUES 
(
    'Senior Full Stack Developer',
    'We are looking for an experienced full-stack developer to join our team and work on cutting-edge web applications.',
    '5+ years experience with React, Node.js, Python, PostgreSQL. Strong problem-solving skills and team collaboration.',
    'San Francisco, CA',
    120000,
    180000,
    'full-time',
    'senior',
    true,
    1,
    1
),
(
    'Frontend Developer Intern',
    'Great opportunity for a computer science student to gain real-world experience in frontend development.',
    'Basic knowledge of HTML, CSS, JavaScript. Familiarity with React is a plus. Currently enrolled in CS program.',
    'Remote',
    2000,
    3000,
    'internship',
    'entry',
    true,
    1,
    1
) ON CONFLICT DO NOTHING;
