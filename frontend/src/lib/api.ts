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
  config => {
    // Get token from localStorage and add to Authorization header
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  response => response,
  error => {
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
  updateUser: (id: number, data: UpdateUserData) =>
    api.put(`/users/${id}`, data),
  deleteUser: (id: number) => api.delete(`/users/${id}`),
  createUser: (data: SignupData) => api.post('/auth/signup', data),
};

// Email verification API endpoints
export const emailAPI = {
  sendOTP: (email: string) => api.post('/email/send-otp', { email }),
  verifyOTP: (email: string, otpCode: string) =>
    api.post('/email/verify-otp', { email, otp_code: otpCode }),
  resendOTP: (email: string) => api.post('/email/resend-otp', { email }),
  sendOTPAuthenticated: () => api.post('/email/send-otp-authenticated'),
  verifyOTPAuthenticated: (otpCode: string) =>
    api.post('/email/verify-otp-authenticated', { otp_code: otpCode }),
};

// Job System API
export const jobAPI = {
  // Company endpoints
  createCompany: (data: CompanyCreate) => api.post('/jobs/companies/', data),
  getCompanies: (page = 1, per_page = 20) =>
    api.get(`/jobs/companies/?page=${page}&per_page=${per_page}`),
  getCompany: (id: number) => api.get(`/jobs/companies/${id}`),

  // Job endpoints
  createJob: (data: JobCreate) => api.post('/jobs/', data),
  getJobs: (params: JobSearchParams = {}) => {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value.toString());
      }
    });
    return api.get(`/jobs/?${searchParams.toString()}`);
  },
  getJob: (id: number) => api.get(`/jobs/${id}`),

  // Job application endpoints
  applyToJob: (jobId: number, data: JobApplicationCreate) =>
    api.post(`/jobs/${jobId}/apply`, data),

  // Health check
  healthCheck: () => api.get('/jobs/health/status'),
};

// Types
export interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'company';
  is_active: boolean;
  is_email_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface SignupData {
  name: string;
  email: string;
  password: string;
  role?: 'admin' | 'user' | 'company';
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
  otp_code?: string; // Include OTP for testing purposes
}

export interface EmailVerificationResponse {
  message: string;
  success: boolean;
}

// Job System Types
export interface Company {
  id: number;
  name: string;
  description?: string;
  website?: string;
  industry?: string;
  size?: string;
  location?: string;
  created_by: number;
  created_at: string;
  updated_at: string;
}

export interface Job {
  id: number;
  title: string;
  description: string;
  requirements?: string;
  location?: string;
  salary_min?: number;
  salary_max?: number;
  employment_type:
    | 'full-time'
    | 'part-time'
    | 'contract'
    | 'internship'
    | 'freelance';
  experience_level: 'entry' | 'mid' | 'senior' | 'executive';
  remote_work: boolean;
  company_id: number;
  posted_by: number;
  is_active: boolean;
  application_deadline?: string;
  created_at: string;
  updated_at: string;
}

export interface JobWithCompany extends Job {
  company: Company;
}

export interface JobApplication {
  id: number;
  job_id: number;
  applicant_id: number;
  cover_letter?: string;
  resume_url?: string;
  status: 'pending' | 'reviewed' | 'accepted' | 'rejected';
  applied_at: string;
  reviewed_at?: string;
  notes?: string;
}

export interface CompanyCreate {
  name: string;
  description?: string;
  website?: string;
  industry?: string;
  size?: string;
  location?: string;
}

export interface JobCreate {
  title: string;
  description: string;
  requirements?: string;
  location?: string;
  salary_min?: number;
  salary_max?: number;
  employment_type:
    | 'full-time'
    | 'part-time'
    | 'contract'
    | 'internship'
    | 'freelance';
  experience_level: 'entry' | 'mid' | 'senior' | 'executive';
  remote_work: boolean;
  company_id: number;
  application_deadline?: string;
}

export interface JobApplicationCreate {
  job_id: number;
  cover_letter?: string;
  resume_url?: string;
}

export interface JobSearchParams {
  query?: string;
  location?: string;
  employment_type?: string;
  experience_level?: string;
  remote_work?: boolean;
  salary_min?: number;
  company_id?: number;
  page?: number;
  per_page?: number;
}

export interface JobListResponse {
  jobs: JobWithCompany[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface CompanyListResponse {
  companies: Company[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}
