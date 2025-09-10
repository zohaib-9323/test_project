# Test Project - Full Stack Application

## 🚀 Features

### Backend (FastAPI + Python 3.13)
- ✅ User authentication with JWT tokens
- ✅ Email verification with OTP
- ✅ File upload with Google Cloud Storage
- ✅ Role-based access control (admin/user)
- ✅ Supabase database integration
- ✅ Comprehensive API endpoints
- ✅ Complete test suite

### Frontend (Next.js + TypeScript)
- ✅ Modern React UI with Tailwind CSS
- ✅ Authentication flow with email verification
- ✅ User profile management
- ✅ Admin panel for user management
- ✅ File upload interface
- ✅ Responsive design

### CI/CD Pipeline (GitHub Actions)
- ✅ Automated testing and linting
- ✅ Security scanning with Trivy
- ✅ Integration tests
- ✅ Deployment pipeline
- ✅ Code quality checks

## 🛠️ Setup

1. **Backend Setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scriptsctivate
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Environment Variables**:
   - Copy `backend/.env.example` to `backend/.env`
   - Configure Supabase and Google Cloud Storage credentials

## 📚 Documentation

- [CI/CD Setup Guide](CICD_IMPROVEMENT_GUIDE.md)
- [Google Cloud Storage Setup](GCS_SETUP_GUIDE.md)
- [Email Setup Guide](EMAIL_SETUP_GUIDE.md)

## 🔗 Links

- **Repository**: https://github.com/zohaib-9323/test_project
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

---
*Last updated: Wed Sep 10 15:10:27 PKT 2025*
# CI/CD Test
