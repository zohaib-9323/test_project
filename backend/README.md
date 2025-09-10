# User Management API

A secure FastAPI-based user management system with JWT authentication and Supabase integration.

## Features

- **Secure Authentication**: JWT-based authentication with password hashing
- **User CRUD Operations**: Create, read, update, and delete users
- **Modular Architecture**: Clean separation of concerns with proper folder structure
- **Input Validation**: Comprehensive data validation using Pydantic
- **Security**: Password strength requirements, secure token handling

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── database.py      # Database configuration
│   │   └── settings.py      # Application settings
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py          # Pydantic models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication routes
│   │   └── users.py         # User CRUD routes
│   ├── services/
│   │   ├── __init__.py
│   │   └── user_service.py  # Business logic layer
│   ├── utils/
│   │   ├── __init__.py
│   │   └── auth.py          # Authentication utilities
│   └── middleware/
│       ├── __init__.py
│       └── auth.py          # Authentication middleware
├── main.py                  # FastAPI application entry point
├── requirements.txt         # Python dependencies
└── .env.example            # Environment variables template
```

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   - Copy `.env.example` to `.env`
   - Fill in your Supabase credentials and JWT secret

3. **Database Setup**:
   - Create a `users` table in your Supabase project with the following schema:
   ```sql
   CREATE TABLE users (
     id SERIAL PRIMARY KEY,
     name VARCHAR(255) NOT NULL,
     email VARCHAR(255) UNIQUE NOT NULL,
     hashed_password VARCHAR(255) NOT NULL,
     is_active BOOLEAN DEFAULT TRUE,
     created_at TIMESTAMP DEFAULT NOW(),
     updated_at TIMESTAMP DEFAULT NOW()
   );
   ```

4. **Run the Application**:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

### Authentication

- `POST /auth/signup` - Register a new user
- `POST /auth/login` - Login and get access token

### User Management (Protected Routes)

- `GET /users/me` - Get current user information
- `GET /users/` - Get all users
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/{user_id}` - Update user information
- `DELETE /users/{user_id}` - Delete user

### Health Check

- `GET /` - Welcome message
- `GET /health` - Health check endpoint

## Security Features

- **Password Hashing**: Uses bcrypt for secure password storage
- **JWT Tokens**: Secure token-based authentication
- **Input Validation**: Comprehensive validation for all inputs
- **Password Requirements**: Minimum 8 characters with uppercase, lowercase, and digits
- **CORS Protection**: Configurable CORS settings
- **Authorization**: Users can only access/modify their own data

## Usage Examples

### Signup
```bash
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

### Get Current User (with token)
```bash
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Environment Variables

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon key
- `SECRET_KEY`: JWT secret key (change in production)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)

## Development

The application uses a modular architecture with clear separation of concerns:

- **Models**: Pydantic models for data validation
- **Services**: Business logic and database operations
- **Routes**: API endpoints and request handling
- **Middleware**: Authentication and authorization
- **Utils**: Helper functions and utilities
- **Config**: Application configuration and settings
