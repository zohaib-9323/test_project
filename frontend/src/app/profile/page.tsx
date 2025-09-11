/**
 * Profile Management Page Component
 *
 * This page provides comprehensive profile management functionality:
 * - Display current user information
 * - Edit profile with form validation
 * - Real-time error handling and success feedback
 * - Loading states and user feedback
 * - Navigation back to dashboard
 *
 * Features include in-place editing, form validation, and proper error handling.
 */

'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  User,
  Mail,
  Calendar,
  Shield,
  Edit3,
  Save,
  X,
  ArrowLeft,
  AlertCircle,
  CheckCircle,
  Loader2,
  Crown,
  UserCheck,
  Upload,
  Download,
} from 'lucide-react';
import Link from 'next/link';
import EmailVerification from '@/components/EmailVerification';
import EmailVerificationGuard from '@/components/EmailVerificationGuard';

const profileSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
});

type ProfileForm = z.infer<typeof profileSchema>;

export default function ProfilePage() {
  const { user, loading, updateUser, logout } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [updateError, setUpdateError] = useState<string | null>(null);
  const [updateSuccess, setUpdateSuccess] = useState(false);

  const form = useForm<ProfileForm>({
    resolver: zodResolver(profileSchema),
    mode: 'onSubmit', // Only validate on submit
    reValidateMode: 'onBlur', // Re-validate on blur after first submit
    defaultValues: {
      name: '',
      email: '',
    },
  });

  // Update form values when user data changes
  useEffect(() => {
    if (user) {
      form.reset({
        name: user.name,
        email: user.email,
      });
    }
  }, [user, form]);

  const handleEdit = () => {
    setIsEditing(true);
    setUpdateError(null);
    setUpdateSuccess(false);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setUpdateError(null);
    setUpdateSuccess(false);
    // Reset form to original values
    if (user) {
      form.reset({
        name: user.name,
        email: user.email,
      });
    }
  };

  const handleSave = async (data: ProfileForm) => {
    if (!user) return;

    setIsUpdating(true);
    setUpdateError(null);
    setUpdateSuccess(false);

    try {
      const success = await updateUser(data);
      if (success) {
        setIsEditing(false);
        setUpdateSuccess(true);
        // Clear success message after 3 seconds
        setTimeout(() => setUpdateSuccess(false), 3000);
      } else {
        setUpdateError('Failed to update profile. Please try again.');
      }
    } catch {
      setUpdateError('An unexpected error occurred. Please try again.');
    } finally {
      setIsUpdating(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl shadow-lg p-8 max-w-md w-full">
          <div className="flex items-center space-x-3 mb-4">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            <span className="text-lg font-medium text-gray-700">Loading profile...</span>
          </div>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl shadow-lg p-8 max-w-md w-full text-center">
          <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h2>
          <p className="text-gray-600 mb-6">You need to be logged in to view this page.</p>
          <Link
            href="/"
            className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-md"
          >
            <ArrowLeft className="h-5 w-5 mr-2" />
            Go to Login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <EmailVerificationGuard>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        {/* Header */}
        <header className="bg-white/80 backdrop-blur-sm shadow-lg border-b border-white/20 sticky top-0 z-40">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <Link
                  href="/"
                  className="flex items-center text-gray-700 hover:text-blue-600 transition-colors font-medium"
                >
                  <ArrowLeft className="h-5 w-5 mr-2" />
                  Back to Dashboard
                </Link>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-700 bg-gray-100 px-3 py-1 rounded-full">
                  Welcome, {user.name}
                </span>
                <button
                  onClick={logout}
                  className="px-4 py-2 text-sm text-gray-700 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors border border-gray-200"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-6xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <div className="space-y-8">
            {/* Page Header */}
            <div className="text-center mb-8">
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
                Profile Settings
              </h1>
              <p className="text-xl text-gray-600">
                Manage your account information and preferences.
              </p>
            </div>

            {/* Success Message */}
            {updateSuccess && (
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-4 shadow-sm">
                <div className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                  <p className="text-sm font-semibold text-green-800">
                    Profile updated successfully!
                  </p>
                </div>
              </div>
            )}

            {/* Error Message */}
            {updateError && (
              <div className="bg-gradient-to-r from-red-50 to-rose-50 border border-red-200 rounded-xl p-4 shadow-sm">
                <div className="flex items-center">
                  <AlertCircle className="h-5 w-5 text-red-500 mr-3" />
                  <p className="text-sm font-semibold text-red-800">
                    {updateError}
                  </p>
                </div>
              </div>
            )}

            {/* Profile Card */}
            <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-bold text-white">
                    Personal Information
                  </h2>
                  {!isEditing && (
                    <button
                      onClick={handleEdit}
                      className="inline-flex items-center px-4 py-2 bg-white/20 text-white hover:bg-white/30 rounded-lg transition-colors backdrop-blur-sm"
                    >
                      <Edit3 className="h-4 w-4 mr-2" />
                      Edit Profile
                    </button>
                  )}
                </div>
              </div>

              <div className="p-8">
                {isEditing ? (
                  <form
                    onSubmit={form.handleSubmit(handleSave)}
                    className="space-y-6"
                  >
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label
                          htmlFor="name"
                          className="block text-sm font-semibold text-gray-700 mb-2"
                        >
                          Full Name
                        </label>
                        <div className="relative">
                          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none top-10">
                            <User className="h-5 w-5 text-gray-400" />
                          </div>
                          <input
                            {...form.register('name')}
                            type="text"
                            className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-white/80"
                            placeholder="Enter your full name"
                          />
                        </div>
                        {form.formState.errors.name && (
                          <p className="mt-1 text-sm text-red-600 flex items-center">
                            <AlertCircle className="h-4 w-4 mr-1" />
                            {form.formState.errors.name.message}
                          </p>
                        )}
                      </div>

                      <div>
                        <label
                          htmlFor="email"
                          className="block text-sm font-semibold text-gray-700 mb-2"
                        >
                          Email Address
                        </label>
                        <div className="relative">
                          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none top-10">
                            <Mail className="h-5 w-5 text-gray-400" />
                          </div>
                          <input
                            {...form.register('email')}
                            type="email"
                            className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-white/80"
                            placeholder="Enter your email"
                          />
                        </div>
                        {form.formState.errors.email && (
                          <p className="mt-1 text-sm text-red-600 flex items-center">
                            <AlertCircle className="h-4 w-4 mr-1" />
                            {form.formState.errors.email.message}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="flex justify-end space-x-3 pt-4 border-t border-gray-100">
                      <button
                        type="button"
                        onClick={handleCancel}
                        disabled={isUpdating}
                        className="inline-flex items-center px-6 py-3 border border-gray-300 shadow-sm text-sm font-semibold rounded-xl text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        <X className="h-4 w-4 mr-2" />
                        Cancel
                      </button>
                      <button
                        type="submit"
                        disabled={isUpdating}
                        className="inline-flex items-center px-6 py-3 border border-transparent shadow-sm text-sm font-semibold rounded-xl text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                      >
                        {isUpdating ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Saving...
                          </>
                        ) : (
                          <>
                            <Save className="h-4 w-4 mr-2" />
                            Save Changes
                          </>
                        )}
                      </button>
                    </div>
                  </form>
                ) : (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                      <div className="space-y-4">
                        <label className="block text-sm font-semibold text-gray-700">
                          Full Name
                        </label>
                        <div className="flex items-center p-4 bg-gray-50 rounded-xl">
                          <User className="h-6 w-6 text-blue-500 mr-3 flex-shrink-0" />
                          <p className="text-lg font-medium text-gray-900">{user.name}</p>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <label className="block text-sm font-semibold text-gray-700">
                          Email Address
                        </label>
                        <div className="flex items-center p-4 bg-gray-50 rounded-xl">
                          <Mail className="h-6 w-6 text-green-500 mr-3 flex-shrink-0" />
                          <p className="text-lg font-medium text-gray-900">{user.email}</p>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <label className="block text-sm font-semibold text-gray-700">
                          User ID
                        </label>
                        <div className="flex items-center p-4 bg-gray-50 rounded-xl">
                          <Shield className="h-6 w-6 text-gray-500 mr-3 flex-shrink-0" />
                          <p className="text-lg font-medium text-gray-900">#{user.id}</p>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <label className="block text-sm font-semibold text-gray-700">
                          Role
                        </label>
                        <div className="flex items-center p-4 bg-gray-50 rounded-xl">
                          {user.role === 'admin' ? (
                            <Crown className="h-6 w-6 text-yellow-500 mr-3 flex-shrink-0" />
                          ) : (
                            <UserCheck className="h-6 w-6 text-blue-500 mr-3 flex-shrink-0" />
                          )}
                          <span
                            className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${
                              user.role === 'admin'
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-blue-100 text-blue-800'
                            }`}
                          >
                            {user.role === 'admin'
                              ? 'Administrator'
                              : 'Standard User'}
                          </span>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <label className="block text-sm font-semibold text-gray-700">
                          Member Since
                        </label>
                        <div className="flex items-center p-4 bg-gray-50 rounded-xl">
                          <Calendar className="h-6 w-6 text-purple-500 mr-3 flex-shrink-0" />
                          <p className="text-lg font-medium text-gray-900">
                            {new Date(user.created_at).toLocaleDateString(
                              'en-US',
                              {
                                year: 'numeric',
                                month: 'long',
                                day: 'numeric',
                              }
                            )}
                          </p>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <label className="block text-sm font-semibold text-gray-700">
                          Account Status
                        </label>
                        <div className="flex items-center p-4 bg-gray-50 rounded-xl">
                          <span
                            className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${
                              user.is_active
                                ? 'bg-green-100 text-green-800'
                                : 'bg-red-100 text-red-800'
                            }`}
                          >
                            {user.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-6 border-t border-gray-100">
                      <div className="space-y-4">
                        <label className="block text-sm font-semibold text-gray-700">
                          Last Updated
                        </label>
                        <div className="flex items-center p-4 bg-gray-50 rounded-xl">
                          <p className="text-lg font-medium text-gray-900">
                            {new Date(user.updated_at).toLocaleDateString('en-US', {
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </p>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <label className="block text-sm font-semibold text-gray-700">
                          Account Type
                        </label>
                        <div className="flex items-center p-4 bg-gray-50 rounded-xl">
                          <p className="text-lg font-medium text-gray-900">
                            Standard User
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Email Verification */}
            <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
              <div className="bg-gradient-to-r from-green-600 to-teal-600 px-6 py-4">
                <h2 className="text-xl font-bold text-white">
                  Email Verification
                </h2>
              </div>
              <div className="p-8">
                <EmailVerification
                  email={user.email}
                  isVerified={user.is_email_verified}
                  onVerificationSuccess={() => {
                    // Refresh user data after successful verification
                    window.location.reload();
                  }}
                  isAuthenticated={true}
                />
              </div>
            </div>

            {/* Download Profile Data */}
            <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Download Profile Data
                </h3>
                <p className="text-gray-600 mb-6">
                  Export your profile information for backup or sharing.
                </p>
                <button className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-colors shadow-lg">
                  <Download className="h-5 w-5 mr-2" />
                  Download Profile JSON
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </EmailVerificationGuard>
  );
}
