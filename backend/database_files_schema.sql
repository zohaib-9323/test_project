-- Database Schema for File Upload System
-- Run this in your Supabase SQL editor

-- Create files table for storing file metadata
CREATE TABLE IF NOT EXISTS files (
    id VARCHAR(255) PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(20) NOT NULL CHECK (file_type IN ('image', 'document', 'video', 'audio', 'other')),
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    access_level VARCHAR(20) NOT NULL DEFAULT 'private' CHECK (access_level IN ('private', 'public', 'restricted')),
    gcs_bucket VARCHAR(255),
    gcs_path VARCHAR(500),
    upload_url TEXT NOT NULL,
    download_url TEXT NOT NULL,
    thumbnail_url TEXT,
    description TEXT,
    tags TEXT[], -- Array of tags
    uploaded_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_files_uploaded_by ON files(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_files_file_type ON files(file_type);
CREATE INDEX IF NOT EXISTS idx_files_access_level ON files(access_level);
CREATE INDEX IF NOT EXISTS idx_files_uploaded_at ON files(uploaded_at);
CREATE INDEX IF NOT EXISTS idx_files_is_active ON files(is_active);
CREATE INDEX IF NOT EXISTS idx_files_tags ON files USING GIN(tags);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_files_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS update_files_updated_at ON files;
CREATE TRIGGER update_files_updated_at
    BEFORE UPDATE ON files
    FOR EACH ROW
    EXECUTE FUNCTION update_files_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE files ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for file access control

-- Policy: Users can view their own files
CREATE POLICY "Users can view their own files" ON files
    FOR SELECT USING (uploaded_by = auth.uid()::integer);

-- Policy: Users can view public files
CREATE POLICY "Anyone can view public files" ON files
    FOR SELECT USING (access_level = 'public' AND is_active = true);

-- Policy: Users can view restricted files if authenticated
CREATE POLICY "Authenticated users can view restricted files" ON files
    FOR SELECT USING (access_level = 'restricted' AND auth.uid() IS NOT NULL AND is_active = true);

-- Policy: Users can insert their own files
CREATE POLICY "Users can insert their own files" ON files
    FOR INSERT WITH CHECK (uploaded_by = auth.uid()::integer);

-- Policy: Users can update their own files
CREATE POLICY "Users can update their own files" ON files
    FOR UPDATE USING (uploaded_by = auth.uid()::integer);

-- Policy: Users can delete their own files
CREATE POLICY "Users can delete their own files" ON files
    FOR DELETE USING (uploaded_by = auth.uid()::integer);

-- Create a view for public files (for easier querying)
CREATE OR REPLACE VIEW public_files AS
SELECT 
    id,
    filename,
    original_filename,
    file_type,
    file_size,
    mime_type,
    download_url,
    thumbnail_url,
    description,
    tags,
    uploaded_at
FROM files 
WHERE access_level = 'public' AND is_active = true;

-- Grant permissions on the view
GRANT SELECT ON public_files TO anon, authenticated;

-- Create a function to get user's file statistics
CREATE OR REPLACE FUNCTION get_user_file_stats(user_id INTEGER)
RETURNS TABLE (
    total_files BIGINT,
    total_size BIGINT,
    files_by_type JSONB,
    files_by_access JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_files,
        COALESCE(SUM(file_size), 0) as total_size,
        jsonb_object_agg(file_type, type_count) as files_by_type,
        jsonb_object_agg(access_level, access_count) as files_by_access
    FROM (
        SELECT 
            file_type,
            COUNT(*) as type_count
        FROM files 
        WHERE uploaded_by = user_id AND is_active = true
        GROUP BY file_type
    ) type_stats
    CROSS JOIN (
        SELECT 
            access_level,
            COUNT(*) as access_count
        FROM files 
        WHERE uploaded_by = user_id AND is_active = true
        GROUP BY access_level
    ) access_stats;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission on the function
GRANT EXECUTE ON FUNCTION get_user_file_stats(INTEGER) TO authenticated;

-- Create a function to clean up expired files
CREATE OR REPLACE FUNCTION cleanup_expired_files()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Soft delete expired files
    UPDATE files 
    SET is_active = false 
    WHERE expires_at IS NOT NULL 
    AND expires_at < NOW() 
    AND is_active = true;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission on the cleanup function
GRANT EXECUTE ON FUNCTION cleanup_expired_files() TO authenticated;

-- Insert some sample data (optional - for testing)
-- INSERT INTO files (
--     id, filename, original_filename, file_type, file_size, mime_type,
--     access_level, upload_url, download_url, uploaded_by
-- ) VALUES (
--     'sample-file-1', 'sample-1.jpg', 'sample-image.jpg', 'image', 1024000,
--     'image/jpeg', 'public', 'gs://bucket/sample-1.jpg', 'https://storage.googleapis.com/bucket/sample-1.jpg', 1
-- );

-- Create a comment on the table
COMMENT ON TABLE files IS 'Stores metadata for uploaded files including Google Cloud Storage references';
COMMENT ON COLUMN files.gcs_bucket IS 'Google Cloud Storage bucket name';
COMMENT ON COLUMN files.gcs_path IS 'Path to file in Google Cloud Storage';
COMMENT ON COLUMN files.tags IS 'Array of tags for categorizing files';
COMMENT ON COLUMN files.expires_at IS 'Optional expiration date for temporary files';

