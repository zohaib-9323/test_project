/**
 * Email Verification Guard Component
 *
 * This component protects routes that require verified email:
 * - Checks if user is authenticated
 * - Checks if user's email is verified
 * - Redirects to email verification page if not verified
 * - Shows loading state while checking
 * - Renders children only if email is verified
 *
 * Used to wrap pages that require email verification.
 */

'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Loader2, AlertCircle, Shield, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

interface EmailVerificationGuardProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export default function EmailVerificationGuard({
  children,
  fallback,
}: EmailVerificationGuardProps) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    if (!loading) {
      setIsChecking(false);

      // If user is not authenticated, redirect to login
      if (!user) {
        router.push('/');
        return;
      }

      // If user is authenticated but email is not verified, redirect to verification
      if (user && !user.is_email_verified) {
        router.push(`/verify-email?email=${encodeURIComponent(user.email)}`);
        return;
      }
    }
  }, [user, loading, router]);

  // Show loading state while checking authentication
  if (loading || isChecking) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          <span className="text-gray-600">Checking email verification...</span>
        </div>
      </div>
    );
  }

  // If user is not authenticated, show access denied
  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Access Denied
          </h2>
          <p className="text-gray-600 mb-4">
            You need to be logged in to access this page.
          </p>
          <Link
            href="/"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Go to Login
          </Link>
        </div>
      </div>
    );
  }

  // If user is authenticated but email is not verified, show verification required
  if (user && !user.is_email_verified) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Shield className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Email Verification Required
          </h2>
          <p className="text-gray-600 mb-4">
            Please verify your email address to access this page.
          </p>
          <p className="text-sm text-gray-500 mb-6">
            Verification code sent to:{' '}
            <span className="font-medium">{user.email}</span>
          </p>
          <Link
            href={`/verify-email?email=${encodeURIComponent(user.email)}`}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            <Shield className="h-4 w-4 mr-2" />
            Verify Email
          </Link>
        </div>
      </div>
    );
  }

  // If custom fallback is provided, use it
  if (fallback) {
    return <>{fallback}</>;
  }

  // User is authenticated and email is verified, render children
  return <>{children}</>;
}
