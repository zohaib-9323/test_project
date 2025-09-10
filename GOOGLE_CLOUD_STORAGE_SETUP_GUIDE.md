# 📁 Google Cloud Storage Setup Guide

## Overview
This guide will help you set up Google Cloud Storage for file upload functionality in your application. The system supports file uploads with metadata, access control, and secure signed URLs.

## 🚀 Quick Start

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note your **Project ID**

### 2. Enable Google Cloud Storage API
1. In Google Cloud Console, go to **APIs & Services** > **Library**
2. Search for "Cloud Storage API"
3. Click **Enable**

### 3. Create Storage Bucket
1. Go to **Cloud Storage** > **Buckets**
2. Click **Create Bucket**
3. Choose a unique bucket name (e.g., `your-app-files-2024`)
4. Select region (choose closest to your users)
5. Choose storage class (Standard is fine for most use cases)
6. Set access control to **Uniform**
7. Click **Create**

### 4. Create Service Account
1. Go to **IAM & Admin** > **Service Accounts**
2. Click **Create Service Account**
3. Enter name: `file-upload-service`
4. Enter description: `Service account for file upload operations`
5. Click **Create and Continue**
6. Grant roles:
   - **Storage Object Admin** (for full file operations)
   - **Storage Legacy Bucket Reader** (for bucket access)
7. Click **Continue** and **Done**

### 5. Generate Service Account Key
1. Click on your service account
2. Go to **Keys** tab
3. Click **Add Key** > **Create New Key**
4. Choose **JSON** format
5. Click **Create**
6. **IMPORTANT**: Save the downloaded JSON file securely

## 🔧 Environment Configuration

### Add to your `.env` file:

```env
# Google Cloud Storage Configuration
GCS_PROJECT_ID=your-project-id-here
GCS_BUCKET_NAME=your-bucket-name-here
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json

# Alternative: Use service account key as environment variable
# GCS_SERVICE_ACCOUNT_KEY={"type":"service_account","project_id":"..."}
```

### Option 1: Service Account Key File (Recommended for Development)
```env
GCS_PROJECT_ID=my-app-project-123
GCS_BUCKET_NAME=my-app-files-2024
GOOGLE_APPLICATION_CREDENTIALS=/Users/yourname/Downloads/service-account-key.json
```

### Option 2: Service Account Key as Environment Variable (Recommended for Production)
```env
GCS_PROJECT_ID=my-app-project-123
GCS_BUCKET_NAME=my-app-files-2024
GCS_SERVICE_ACCOUNT_KEY={"type":"service_account","project_id":"my-app-project-123","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"file-upload-service@my-app-project-123.iam.gserviceaccount.com","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/file-upload-service%40my-app-project-123.iam.gserviceaccount.com"}
```

## 🗄️ Database Setup

### Run the SQL Schema
1. Go to your Supabase dashboard
2. Navigate to **SQL Editor**
3. Copy and paste the contents of `database_files_schema.sql`
4. Click **Run**

This will create:
- `files` table for file metadata
- Indexes for performance
- Row Level Security policies
- Helper functions for file statistics

## 🧪 Testing the Setup

### 1. Test File Upload
```bash
# Create a test file
echo "Hello, World!" > test.txt

# Upload file using curl
curl -X POST http://localhost:8000/files/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@test.txt" \
  -F "description=Test file upload" \
  -F "access_level=private" \
  -F "tags=test,demo"
```

### 2. Test File Listing
```bash
# List user's files
curl -X GET http://localhost:8000/files/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 3. Test File Download
```bash
# Get file download URL
curl -X GET http://localhost:8000/files/{file_id}/download \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 📋 API Endpoints

### File Upload
- **POST** `/files/upload`
- **Parameters**: `file`, `description`, `access_level`, `tags`
- **Access**: Authenticated users only

### File Management
- **GET** `/files/` - List user's files
- **GET** `/files/{file_id}` - Get file details
- **PUT** `/files/{file_id}` - Update file metadata
- **DELETE** `/files/{file_id}` - Delete file

### Public Files
- **GET** `/files/public/` - List public files (no auth required)

### File Search
- **GET** `/files/search/?q=query` - Search files

### File Download
- **GET** `/files/{file_id}/download` - Get download URL

## 🔒 Security Features

### Access Levels
- **Private**: Only file owner can access
- **Public**: Anyone with link can access
- **Restricted**: Only authenticated users can access

### File Validation
- Maximum file size: 10MB
- MIME type detection
- File type categorization (image, document, video, audio, other)

### Signed URLs
- Private files use signed URLs with expiration
- Public files use direct URLs
- Automatic URL regeneration for expired links

## 🚨 Troubleshooting

### Common Issues

#### 1. "Google Cloud Storage not configured"
- Check that `GCS_PROJECT_ID` and `GCS_BUCKET_NAME` are set
- Verify service account key is accessible

#### 2. "Failed to connect to Google Cloud Storage"
- Check service account permissions
- Verify bucket exists and is accessible
- Ensure API is enabled

#### 3. "Access denied" errors
- Check service account has Storage Object Admin role
- Verify bucket permissions
- Check IAM policies

#### 4. File upload fails
- Check file size (10MB limit)
- Verify file is not corrupted
- Check network connectivity

### Debug Mode
Add to your `.env` for detailed logging:
```env
GOOGLE_CLOUD_LOGGING_LEVEL=DEBUG
```

## 📊 File Statistics

The system provides file statistics via the `get_user_file_stats()` function:

```sql
SELECT * FROM get_user_file_stats(1);
```

Returns:
- Total files count
- Total storage used
- Files by type breakdown
- Files by access level breakdown

## 🔄 File Lifecycle

### Upload Process
1. File validation (size, type)
2. Generate unique file ID
3. Upload to Google Cloud Storage
4. Store metadata in database
5. Generate access URLs

### Access Process
1. Check file permissions
2. Generate appropriate URL (public/signed)
3. Return download URL to client

### Deletion Process
1. Soft delete in database (`is_active = false`)
2. Delete from Google Cloud Storage
3. Clean up any thumbnails

## 🎯 Production Considerations

### 1. Security
- Use environment variables for credentials
- Implement file type restrictions
- Add virus scanning
- Set up monitoring and alerts

### 2. Performance
- Use CDN for public files
- Implement file caching
- Add thumbnail generation
- Optimize database queries

### 3. Cost Optimization
- Use appropriate storage classes
- Implement file lifecycle policies
- Monitor storage usage
- Set up cost alerts

### 4. Backup
- Enable bucket versioning
- Set up cross-region replication
- Implement backup policies

## 📝 Example Usage

### Frontend Integration
```javascript
// Upload file
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('description', 'My uploaded file');
formData.append('access_level', 'private');
formData.append('tags', 'work,important');

const response = await fetch('/files/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

const fileData = await response.json();
console.log('File uploaded:', fileData);
```

### File Listing
```javascript
// List user's files
const response = await fetch('/files/?page=1&per_page=20', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const files = await response.json();
console.log('User files:', files);
```

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your Google Cloud setup
3. Check application logs
4. Test with a simple file upload

## 📚 Additional Resources

- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [FastAPI File Upload Guide](https://fastapi.tiangolo.com/tutorial/request-files/)
- [Supabase Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)

