# 📁 Google Cloud Storage Setup Guide

## Overview
This guide will help you set up Google Cloud Storage (GCS) for file upload functionality in your application. The implementation supports secure file uploads, metadata management, and access control.

## 🎯 Features Implemented

✅ **File Upload**: Upload files to Google Cloud Storage  
✅ **File Management**: List, view, and delete files  
✅ **Access Control**: User-based file permissions  
✅ **File Types**: Support for images, documents, videos, audio, and other files  
✅ **Public/Private**: Toggle file visibility  
✅ **Signed URLs**: Secure access to private files  
✅ **File Metadata**: Automatic file type detection and metadata storage  
✅ **Size Limits**: 10MB file size limit (configurable)  
✅ **Organized Storage**: Files organized by date in GCS buckets  

## 🔧 Step 1: Create Google Cloud Project

### 1.1 Create a New Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: `user-management-files`
4. Click "Create"

### 1.2 Enable Required APIs
1. Go to "APIs & Services" → "Library"
2. Search and enable:
   - **Cloud Storage API**
   - **Cloud Storage JSON API**

## 🪣 Step 2: Create Storage Bucket

### 2.1 Create Bucket
1. Go to "Cloud Storage" → "Buckets"
2. Click "Create Bucket"
3. Configure bucket:
   - **Name**: `your-app-files-bucket` (must be globally unique)
   - **Location**: Choose your preferred region
   - **Storage Class**: Standard
   - **Access Control**: Fine-grained
   - **Protection Tools**: None (for development)

### 2.2 Configure Bucket Permissions
1. Click on your bucket name
2. Go to "Permissions" tab
3. Add your service account with "Storage Admin" role

## 🔐 Step 3: Create Service Account

### 3.1 Create Service Account
1. Go to "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Configure:
   - **Name**: `file-upload-service`
   - **Description**: `Service account for file upload functionality`
   - Click "Create and Continue"

### 3.2 Assign Roles
Add these roles to your service account:
- **Storage Admin** (for full bucket access)
- **Storage Object Admin** (for object management)

### 3.3 Create and Download Key
1. Click on your service account
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Choose "JSON" format
5. Click "Create" - this downloads the key file

## 📝 Step 4: Configure Environment Variables

### 4.1 Add to your `.env` file
Add these variables to your `backend/.env` file:

```env
# Google Cloud Storage Configuration
GCS_PROJECT_ID=your-project-id-here
GCS_BUCKET_NAME=your-app-files-bucket
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json

# Alternative: Use service account key content directly
# GCS_SERVICE_ACCOUNT_KEY={"type": "service_account", "project_id": "...", ...}
```

### 4.2 Service Account Key Options

#### Option A: File Path (Recommended for Development)
```env
GOOGLE_APPLICATION_CREDENTIALS=/Users/faiztoufiq/Desktop/test_project/backend/service-account-key.json
```

#### Option B: Key Content (Recommended for Production)
```env
GCS_SERVICE_ACCOUNT_KEY={"type": "service_account", "project_id": "your-project", "private_key_id": "...", "private_key": "...", "client_email": "...", "client_id": "...", "auth_uri": "...", "token_uri": "...", "auth_provider_x509_cert_url": "...", "client_x509_cert_url": "..."}
```

## 🧪 Step 5: Test the Setup

### 5.1 Check Service Health
```bash
curl http://localhost:8000/files/health/status
```

Expected response:
```json
{
  "service": "file_upload",
  "status": "healthy",
  "gcs_configured": true,
  "bucket_name": "your-app-files-bucket",
  "project_id": "your-project-id"
}
```

### 5.2 Test File Upload
```bash
# Create a test file
echo "Hello, World!" > test.txt

# Upload the file
curl -X POST http://localhost:8000/files/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@test.txt" \
  -F "is_public=false"
```

Expected response:
```json
{
  "message": "File uploaded successfully",
  "success": true,
  "file_id": "uuid-here",
  "file_name": "test.txt",
  "file_url": "https://storage.googleapis.com/...",
  "file_size": 13,
  "file_type": "document",
  "uploaded_at": "2024-01-01T12:00:00Z"
}
```

## 📚 API Endpoints

### Upload File
```http
POST /files/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>

Form Data:
- file: <file>
- is_public: boolean (optional, default: false)
```

### List Files
```http
GET /files/?page=1&per_page=20&file_type=image
Authorization: Bearer <token>
```

### Get File Info
```http
GET /files/{file_id}
Authorization: Bearer <token>
```

### Delete File
```http
DELETE /files/{file_id}
Authorization: Bearer <token>
```

### Download File
```http
GET /files/download/{file_id}
Authorization: Bearer <token>
```

## 🔒 Security Features

### Access Control
- Users can only access files they uploaded
- Private files use signed URLs (1-hour expiration)
- Public files are accessible via public URLs

### File Validation
- File size limit: 10MB (configurable)
- Content type validation
- File type detection (image, document, video, audio, other)

### Storage Organization
```
bucket/
└── files/
    └── 2024/
        └── 01/
            └── 15/
                ├── uuid1_filename1.jpg
                ├── uuid2_document.pdf
                └── uuid3_video.mp4
```

## 🚀 Production Considerations

### 1. Environment Variables
Use environment-specific configurations:
```env
# Development
GCS_BUCKET_NAME=dev-files-bucket
GCS_PROJECT_ID=dev-project

# Production
GCS_BUCKET_NAME=prod-files-bucket
GCS_PROJECT_ID=prod-project
```

### 2. Service Account Permissions
For production, use minimal required permissions:
- **Storage Object Creator** (for uploads)
- **Storage Object Viewer** (for downloads)
- **Storage Object Admin** (for deletions)

### 3. Bucket Configuration
- Enable versioning for file recovery
- Set up lifecycle policies for cost optimization
- Configure CORS for web uploads
- Enable logging and monitoring

### 4. Security
- Use signed URLs for private files
- Implement rate limiting
- Add virus scanning
- Use HTTPS only

## 🛠️ Troubleshooting

### Common Issues

#### 1. "Service account not found"
- Verify the service account key file path
- Check if the key file exists and is readable
- Ensure the service account has proper permissions

#### 2. "Bucket not found"
- Verify the bucket name in environment variables
- Check if the bucket exists in the correct project
- Ensure the service account has access to the bucket

#### 3. "Permission denied"
- Check service account roles
- Verify bucket permissions
- Ensure the service account is added to the bucket

#### 4. "File upload failed"
- Check file size limits
- Verify content type is allowed
- Check network connectivity to GCS

### Debug Commands
```bash
# Check service status
curl http://localhost:8000/files/health/status

# Test with verbose output
curl -v -X POST http://localhost:8000/files/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.txt"

# Check backend logs
tail -f backend/server.log
```

## 📋 Environment Variables Summary

Add these to your `backend/.env` file:

```env
# Required
GCS_PROJECT_ID=your-project-id
GCS_BUCKET_NAME=your-bucket-name

# Choose one authentication method:
# Option 1: Service account key file
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Option 2: Service account key content (for production)
GCS_SERVICE_ACCOUNT_KEY={"type": "service_account", ...}
```

## 🎉 Next Steps

1. **Set up your Google Cloud project** following steps 1-3
2. **Configure environment variables** in your `.env` file
3. **Test the setup** using the provided commands
4. **Integrate with frontend** for file upload UI
5. **Deploy to production** with proper security configurations

The file upload functionality is now ready to use! 🚀

