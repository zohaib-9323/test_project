-- Database Schema Updates for Role-Based Authentication and Email Verification
-- Run this in your Supabase SQL editor

-- 1. Add role column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('admin', 'user'));

-- 2. Add email verification columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_email_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_expires_at TIMESTAMP WITH TIME ZONE;

-- 3. Create OTP table for email verification
CREATE TABLE IF NOT EXISTS email_otps (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    otp_code VARCHAR(6) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_email_verified ON users(is_email_verified);
CREATE INDEX IF NOT EXISTS idx_email_otps_email ON email_otps(email);
CREATE INDEX IF NOT EXISTS idx_email_otps_expires_at ON email_otps(expires_at);
CREATE INDEX IF NOT EXISTS idx_email_otps_is_used ON email_otps(is_used);

-- 5. Create function to automatically update updated_at timestamp for email_otps
CREATE OR REPLACE FUNCTION update_email_otps_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 6. Create trigger to automatically update updated_at for email_otps
DROP TRIGGER IF EXISTS update_email_otps_updated_at ON email_otps;
CREATE TRIGGER update_email_otps_updated_at 
    BEFORE UPDATE ON email_otps 
    FOR EACH ROW 
    EXECUTE FUNCTION update_email_otps_updated_at_column();

-- 7. Create function to clean up expired OTPs (optional - for maintenance)
CREATE OR REPLACE FUNCTION cleanup_expired_otps()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM email_otps 
    WHERE expires_at < NOW() OR is_used = TRUE;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ language 'plpgsql';

-- 8. Update existing users to have default role and email verification status
UPDATE users SET role = 'user' WHERE role IS NULL;
UPDATE users SET is_email_verified = TRUE WHERE is_email_verified IS NULL;

-- 9. Set one user as admin (you can change the email as needed)
UPDATE users SET role = 'admin' WHERE email = 'admin@example.com';

-- 10. Add comments for documentation
COMMENT ON COLUMN users.role IS 'User role: admin or user';
COMMENT ON COLUMN users.is_email_verified IS 'Whether the user has verified their email address';
COMMENT ON COLUMN users.email_verification_token IS 'Token for email verification (UUID)';
COMMENT ON COLUMN users.email_verification_expires_at IS 'Expiration time for email verification token';
COMMENT ON TABLE email_otps IS 'Stores OTP codes for email verification';
COMMENT ON COLUMN email_otps.otp_code IS '6-digit OTP code for email verification';
COMMENT ON COLUMN email_otps.expires_at IS 'When the OTP expires (typically 10 minutes)';
COMMENT ON COLUMN email_otps.is_used IS 'Whether the OTP has been used for verification';

-- 11. Create a view for active users (optional)
CREATE OR REPLACE VIEW active_verified_users AS
SELECT 
    id,
    name,
    email,
    role,
    is_active,
    is_email_verified,
    created_at,
    updated_at
FROM users 
WHERE is_active = TRUE AND is_email_verified = TRUE;

-- 12. Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON email_otps TO authenticated;
-- GRANT USAGE ON SEQUENCE email_otps_id_seq TO authenticated;
