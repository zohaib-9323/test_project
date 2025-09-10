# User Management System

A full-stack user management application with secure authentication, built with FastAPI (backend) and Next.js (frontend).

## 🚀 Features

### Backend (FastAPI)
- **Secure Authentication**: JWT-based authentication with password hashing
- **User CRUD Operations**: Create, read, update, and delete users
- **Modular Architecture**: Clean separation of concerns
- **Input Validation**: Comprehensive data validation using Pydantic
- **Security**: Password strength requirements, secure token handling
- **Mock Database**: In-memory database for testing without external dependencies

### Frontend (Next.js)
- **Modern UI**: Beautiful, responsive interface built with Tailwind CSS
- **Authentication Flow**: Complete signup/login functionality
- **User Profile Management**: View and edit user information
- **Real-time Updates**: Instant feedback with toast notifications
- **Form Validation**: Client-side validation with Zod schemas
- **Type Safety**: Full TypeScript support

## 🏗️ Architecture

```
test_project/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── config/         # Configuration files
│   │   ├── models/         # Pydantic models
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── utils/          # Helper functions
│   │   └── middleware/     # Authentication middleware
│   ├── main.py             # FastAPI application
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js app directory
│   │   ├── contexts/      # React contexts
│   │   └── lib/           # API client and utilities
│   └── package.json       # Node.js dependencies
└── test_integration.py    # Integration test script
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation and settings management
- **JWT**: JSON Web Tokens for authentication
- **bcrypt**: Password hashing
- **Uvicorn**: ASGI server

### Frontend
- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **React Hook Form**: Form handling
- **Zod**: Schema validation
- **Axios**: HTTP client
- **React Hot Toast**: Toast notifications
- **Lucide React**: Icon library

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+
- npm or yarn

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the backend server**:
   ```bash
   python3 -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

## 🧪 Testing

### Integration Tests

Run the comprehensive integration test suite:

```bash
# Install requests if not already installed
pip3 install requests

# Run integration tests
python3 test_integration.py
```

This will test:
- Backend health and connectivity
- Frontend accessibility
- Complete authentication flow
- All API endpoints
- User management operations

### Manual Testing

1. **Signup**: Create a new account with name, email, and password
2. **Login**: Sign in with your credentials
3. **Profile Management**: View and edit your profile information
4. **API Status**: Check the real-time API status indicators

## 📡 API Endpoints

### Authentication
- `POST /auth/signup` - Register a new user
- `POST /auth/login` - Login and get access token

### User Management (Protected)
- `GET /users/me` - Get current user information
- `GET /users/` - Get all users
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/{user_id}` - Update user information
- `DELETE /users/{user_id}` - Delete user

### Health Check
- `GET /` - Welcome message
- `GET /health` - Health check endpoint

## 🔒 Security Features

- **Password Hashing**: Uses bcrypt for secure password storage
- **JWT Tokens**: Secure token-based authentication
- **Input Validation**: Comprehensive validation for all inputs
- **Password Requirements**: Minimum 8 characters with complexity requirements
- **CORS Protection**: Configurable CORS settings
- **Authorization**: Users can only access/modify their own data

## 🎨 UI Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark/Light Mode**: Automatic theme detection
- **Form Validation**: Real-time validation with helpful error messages
- **Loading States**: Smooth loading indicators
- **Toast Notifications**: User-friendly feedback messages
- **Profile Editing**: In-place editing with save/cancel options
- **API Status**: Real-time connection status indicators

## 🔧 Configuration

### Backend Configuration

The backend uses a mock database by default for easy testing. To use a real database:

1. Create a `.env` file in the backend directory
2. Add your database configuration:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   SECRET_KEY=your_jwt_secret_key
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

### Frontend Configuration

The frontend is configured to connect to the backend at `http://localhost:8000`. To change this:

1. Edit `src/lib/api.ts`
2. Update the `API_BASE_URL` constant

## 📊 Project Status

✅ **Backend**: Fully functional with all API endpoints  
✅ **Frontend**: Complete UI with authentication  
✅ **Integration**: Frontend and backend communicating successfully  
✅ **Testing**: Comprehensive test suite passing  
✅ **Documentation**: Complete setup and usage instructions  

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the integration tests
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Support

If you encounter any issues:

1. Check that both backend and frontend servers are running
2. Verify the integration tests pass
3. Check the browser console for any frontend errors
4. Review the backend logs for any server errors

---

**Happy coding! 🎉**
# test_project
