/**
 * Authentication Context Provider
 * 
 * This context provides authentication state and methods throughout the application:
 * - User authentication state management
 * - Login, signup, and logout functionality
 * - User profile updates
 * - Token management and persistence
 * - Error handling with toast notifications
 * 
 * The context automatically handles token storage and user state synchronization.
 */

'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, authAPI, userAPI } from '@/lib/api';
import toast from 'react-hot-toast';

// Authentication context interface
interface AuthContextType {
  user: User | null;                    // Current authenticated user
  loading: boolean;                     // Loading state for authentication
  login: (email: string, password: string) => Promise<boolean>;     // Login method
  signup: (name: string, email: string, password: string) => Promise<boolean>;  // Signup method
  logout: () => void;                   // Logout method
  updateUser: (data: { name?: string; email?: string }) => Promise<boolean>;  // Update user profile
  refreshUser: () => Promise<void>;     // Refresh user data from server
}

// Create authentication context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('token');
      const tokenExpiry = localStorage.getItem('tokenExpiry');
      
      // Check if token exists and hasn't expired
      if (token && tokenExpiry) {
        const now = Date.now();
        const expiry = parseInt(tokenExpiry);
        
        if (now < expiry) {
          // Token is still valid, try to get user data
          try {
            const response = await userAPI.getCurrentUser();
            setUser(response.data);
          } catch {
            // Token might be invalid on server, clear local storage
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            localStorage.removeItem('tokenExpiry');
          }
        } else {
          // Token has expired, clear local storage
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          localStorage.removeItem('tokenExpiry');
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const response = await authAPI.login({ email, password });
      const { access_token } = response.data;
      
      // Store token and calculate expiry (2 days from now)
      const expiryTime = Date.now() + (2 * 24 * 60 * 60 * 1000); // 2 days in milliseconds
      localStorage.setItem('token', access_token);
      localStorage.setItem('tokenExpiry', expiryTime.toString());
      
      // Get user data
      const userResponse = await userAPI.getCurrentUser();
      setUser(userResponse.data);
      localStorage.setItem('user', JSON.stringify(userResponse.data));
      
      toast.success('Login successful!');
      return true;
    } catch (error: unknown) {
      let errorMessage = 'Login failed';
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { data?: { detail?: string } } };
        errorMessage = axiosError.response?.data?.detail || 'Login failed';
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      toast.error(String(errorMessage));
      return false;
    }
  };

  const signup = async (name: string, email: string, password: string): Promise<boolean> => {
    try {
      await authAPI.signup({ name, email, password });
      toast.success('Account created successfully! Please login.');
      return true;
    } catch (error: unknown) {
      let errorMessage = 'Signup failed';
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { data?: { detail?: string } } };
        errorMessage = axiosError.response?.data?.detail || 'Signup failed';
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      toast.error(String(errorMessage));
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('tokenExpiry');
    setUser(null);
    toast.success('Logged out successfully');
    // Redirect to login page
    window.location.href = '/';
  };

  const updateUser = async (data: { name?: string; email?: string }): Promise<boolean> => {
    if (!user) return false;
    
    try {
      const response = await userAPI.updateUser(user.id, data);
      setUser(response.data);
      localStorage.setItem('user', JSON.stringify(response.data));
      toast.success('Profile updated successfully!');
      return true;
    } catch (error: unknown) {
      let errorMessage = 'Update failed';
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { data?: { detail?: string } } };
        errorMessage = axiosError.response?.data?.detail || 'Update failed';
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      toast.error(String(errorMessage));
      return false;
    }
  };

  const refreshUser = async (): Promise<void> => {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
      const response = await userAPI.getCurrentUser();
      setUser(response.data);
      localStorage.setItem('user', JSON.stringify(response.data));
    } catch (error: unknown) {
      console.error('Failed to refresh user data:', error);
      // Don't show error toast for refresh failures to avoid spam
    }
  };

  const value = {
    user,
    loading,
    login,
    signup,
    logout,
    updateUser,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
