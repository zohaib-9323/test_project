/**
 * API Configuration and Client Setup
 * 
 * This module provides:
 * - Axios HTTP client configuration
 * - Authentication token management
 * - API endpoint definitions for authentication and user management
 * - TypeScript interfaces for API responses
 * 
 * The client automatically includes JWT tokens in requests and handles authentication.
 */

import axios from 'axios';

// Backend API base URL
const API_BASE_URL = 'http://localhost:8000';

// Create configured axios instance
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to automatically include JWT token
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage and add to Authorization header
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token is invalid or expired - clear session data
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('tokenExpiry');
      
      // Only redirect if we're not already on the main page
      if (window.location.pathname !== '/') {
        window.location.href = '/';
      }
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const authAPI = {
  signup: (data: SignupData) => api.post('/auth/signup', data),
  login: (data: LoginData) => api.post('/auth/login', data),
};

export const userAPI = {
  getCurrentUser: () => api.get('/users/me'),
  getAllUsers: () => api.get('/users/'),
  getUserById: (id: number) => api.get(`/users/${id}`),
  updateUser: (id: number, data: UpdateUserData) => api.put(`/users/${id}`, data),
  deleteUser: (id: number) => api.delete(`/users/${id}`),
  createUser: (data: SignupData) => api.post('/auth/signup', data),
};

// Email verification API endpoints
export const emailAPI = {
  sendOTP: (email: string) => api.post('/email/send-otp', { email }),
  verifyOTP: (email: string, otpCode: string) => api.post('/email/verify-otp', { email, otp_code: otpCode }),
  resendOTP: (email: string) => api.post('/email/resend-otp', { email }),
  sendOTPAuthenticated: () => api.post('/email/send-otp-authenticated'),
  verifyOTPAuthenticated: (otpCode: string) => api.post('/email/verify-otp-authenticated', { otp_code: otpCode }),
};

// Types
export interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'user';
  is_active: boolean;
  is_email_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface SignupData {
  name: string;
  email: string;
  password: string;
  role?: 'admin' | 'user';
}

export interface LoginData {
  email: string;
  password: string;
}

export interface UpdateUserData {
  name?: string;
  email?: string;
  role?: 'admin' | 'user';
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

// Email verification types
export interface OTPResponse {
  message: string;
  success: boolean;
  expires_in_minutes: number;
  otp_code?: string;  // Include OTP for testing purposes
}

export interface EmailVerificationResponse {
  message: string;
  success: boolean;
}
