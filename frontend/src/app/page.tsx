/**
 * Main Dashboard Page Component
 *
 * This is the main dashboard page that:
 * - Shows user profile summary
 * - Provides quick actions and navigation
 * - Redirects unauthenticated users to login
 * - Handles email verification redirects
 *
 * Authentication forms are now handled by separate /login and /signup pages.
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  User,
  LogOut,
  Settings,
  Users,
  UserCheck,
  Crown,
  Shield,
  Mail,
  Briefcase,
  Building2,
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';

export default function Home() {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  // Handle redirects based on authentication state
  useEffect(() => {
    if (!loading) {
      if (!user) {
        // User is not authenticated, redirect to login
        router.push('/login');
      } else if (!user.is_email_verified) {
        // User is authenticated but email not verified, redirect to verification
        router.push(`/verify-email?email=${encodeURIComponent(user.email)}`);
      }
    }
  }, [user, loading, router]);

  // Handle logout
  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await logout();
      router.push('/login');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setIsLoggingOut(false);
    }
  };

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Don't render dashboard if user is not authenticated or not verified (will redirect)
  if (!user || !user.is_email_verified) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <Shield className="h-5 w-5 text-white" />
                </div>
              </div>
              <div className="ml-4">
                <h1 className="text-2xl font-bold text-gray-900">
                  User Management System
                </h1>
                <p className="text-sm text-gray-500">
                  Welcome back, {user.name}!
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={handleLogout}
                disabled={isLoggingOut}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoggingOut ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Logging out...
                  </div>
                ) : (
                  <>
                    <LogOut className="h-4 w-4 mr-2" />
                    Logout
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Welcome Section */}
          <div className="bg-white overflow-hidden shadow rounded-lg mb-6">
            <div className="px-4 py-5 sm:p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">
                Welcome to your Dashboard
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Profile Summary */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <User className="h-8 w-8 text-gray-400" />
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-gray-900">
                        Profile
                      </h3>
                      <p className="text-sm text-gray-500">
                        Manage your account
                      </p>
                    </div>
                  </div>
                  <div className="mt-4 space-y-2">
                    <div className="flex items-center text-sm">
                      <span className="text-gray-500">Name:</span>
                      <span className="ml-2 font-medium text-gray-900">
                        {user.name}
                      </span>
                    </div>
                    <div className="flex items-center text-sm">
                      <span className="text-gray-500">Email:</span>
                      <span className="ml-2 font-medium text-gray-900">
                        {user.email}
                      </span>
                    </div>
                    <div className="flex items-center text-sm">
                      <span className="text-gray-500">Role:</span>
                      <span
                        className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          user.role === 'admin'
                            ? 'bg-purple-100 text-purple-800'
                            : user.role === 'company'
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-green-100 text-green-800'
                        }`}
                      >
                        {user.role === 'admin' ? (
                          <>
                            <Crown className="h-3 w-3 mr-1" />
                            Admin
                          </>
                        ) : user.role === 'company' ? (
                          <>
                            <Building2 className="h-3 w-3 mr-1" />
                            Company
                          </>
                        ) : (
                          <>
                            <User className="h-3 w-3 mr-1" />
                            User
                          </>
                        )}
                      </span>
                    </div>
                    <div className="flex items-center text-sm">
                      <span className="text-gray-500">Email Verified:</span>
                      <span
                        className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          user.is_email_verified
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {user.is_email_verified ? (
                          <>
                            <UserCheck className="h-3 w-3 mr-1" />
                            Verified
                          </>
                        ) : (
                          <>
                            <Mail className="h-3 w-3 mr-1" />
                            Pending
                          </>
                        )}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Quick Actions */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <Settings className="h-8 w-8 text-gray-400" />
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-gray-900">
                        Quick Actions
                      </h3>
                      <p className="text-sm text-gray-500">Common tasks</p>
                    </div>
                  </div>
                  <div className="mt-4 space-y-2">
                    <Link
                      href="/profile"
                      className="block w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
                    >
                      <User className="h-4 w-4 inline mr-2" />
                      Edit Profile
                    </Link>
                    <Link
                      href="/jobs"
                      className="block w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
                    >
                      <Briefcase className="h-4 w-4 inline mr-2" />
                      Browse Jobs
                    </Link>
                    {user.role === 'admin' && (
                      <Link
                        href="/admin"
                        className="block w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
                      >
                        <Users className="h-4 w-4 inline mr-2" />
                        Admin Panel
                      </Link>
                    )}
                    {(user.role === 'company' || user.role === 'admin') && (
                      <Link
                        href="/company"
                        className="block w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
                      >
                        <Building2 className="h-4 w-4 inline mr-2" />
                        Company Dashboard
                      </Link>
                    )}
                  </div>
                </div>

                {/* System Status */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <Shield className="h-8 w-8 text-gray-400" />
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-gray-900">
                        System Status
                      </h3>
                      <p className="text-sm text-gray-500">Account security</p>
                    </div>
                  </div>
                  <div className="mt-4 space-y-2">
                    <div className="flex items-center text-sm">
                      <div className="h-2 w-2 bg-green-400 rounded-full mr-2"></div>
                      <span className="text-gray-700">Account Active</span>
                    </div>
                    <div className="flex items-center text-sm">
                      <div className="h-2 w-2 bg-green-400 rounded-full mr-2"></div>
                      <span className="text-gray-700">Email Verified</span>
                    </div>
                    <div className="flex items-center text-sm">
                      <div className="h-2 w-2 bg-green-400 rounded-full mr-2"></div>
                      <span className="text-gray-700">Secure Session</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Activity or Additional Content */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">
                Getting Started
              </h2>
              <div className="prose prose-sm text-gray-500">
                <p>Welcome to the User Management System! You can now:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>Update your profile information</li>
                  <li>Manage your account settings</li>
                  {user.role === 'admin' && (
                    <li>Access the admin panel to manage other users</li>
                  )}
                  <li>View your account status and security information</li>
                </ul>
                <p className="mt-4">
                  Use the navigation above to explore different sections of the
                  application.
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
    
  );
}
