/**
 * Email Verification Page
 * 
 * This page handles the email verification flow:
 * - Displays after user signup
 * - Shows OTP input form
 * - Handles verification success/failure
 * - Redirects to dashboard after successful verification
 * - Provides resend functionality
 * 
 * This is a mandatory step in the authentication flow.
 */

'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useState, useEffect, useCallback, Suspense } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { 
  Mail, 
  ArrowLeft, 
  AlertCircle, 
  CheckCircle, 
  Loader2,
  Shield
} from 'lucide-react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { emailAPI, OTPResponse, EmailVerificationResponse } from '@/lib/api';
import toast from 'react-hot-toast';

// Validation schema for OTP input
const otpSchema = z.object({
  otpCode: z.string()
    .min(6, 'OTP must be 6 digits')
    .max(6, 'OTP must be 6 digits')
    .regex(/^\d{6}$/, 'OTP must contain only numbers'),
});

type OTPFormData = z.infer<typeof otpSchema>;

function VerifyEmailContent() {
  const { user, loading, refreshUser } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isLoading, setIsLoading] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [verificationAttempted, setVerificationAttempted] = useState(false);

  // Get email from URL params or user context
  const email = searchParams.get('email') || user?.email || '';

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<OTPFormData>({
    resolver: zodResolver(otpSchema),
  });

  // Countdown timer effect
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (countdown > 0) {
      interval = setInterval(() => {
        setCountdown((prev) => prev - 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [countdown]);

  // Check if user is already verified
  useEffect(() => {
    if (user && user.is_email_verified) {
      router.push('/');
    }
  }, [user, router]);

  // Format countdown display
  const formatCountdown = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Send OTP function
  const sendOTP = useCallback(async () => {
    if (!email) {
      toast.error('Email address not found');
      return;
    }

    setIsLoading(true);
    setVerificationAttempted(true);
    
    try {
      const response = await emailAPI.sendOTP(email);
      const data: OTPResponse = response.data;
      
      if (data.success) {
        setCountdown(data.expires_in_minutes * 60);
        
        // Show OTP in toast for testing purposes
        if (data.otp_code) {
          toast.success(`OTP sent! Code: ${data.otp_code}`, { duration: 10000 });
        } else {
          toast.success(data.message);
        }
      } else {
        toast.error('Failed to send verification code');
      }
    } catch (error: unknown) {
      const errorMessage = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to send verification code';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [email]);

  // Auto-send OTP on page load if email is available
  useEffect(() => {
    if (email && !verificationAttempted) {
      sendOTP();
    }
  }, [email, verificationAttempted, sendOTP]);

  // Verify OTP function
  const verifyOTP = async (data: OTPFormData) => {
    if (!email) {
      toast.error('Email address not found');
      return;
    }

    setIsLoading(true);
    
    try {
      const response = await emailAPI.verifyOTP(email, data.otpCode);
      const result: EmailVerificationResponse = response.data;
      
      if (result.success) {
        toast.success(result.message);
        
        // Refresh user data to get updated verification status
        await refreshUser();
        
        // Redirect to dashboard after a short delay
        setTimeout(() => {
          router.push('/');
        }, 1500);
      } else {
        toast.error('Verification code is invalid or expired');
      }
    } catch (error: unknown) {
      const errorMessage = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Verification failed';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Resend OTP function
  const resendOTP = async () => {
    await sendOTP();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          <span className="text-gray-600">Loading...</span>
        </div>
      </div>
    );
  }

  // If no email is available, redirect to signup
  if (!email) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Email Not Found</h2>
          <p className="text-gray-600 mb-4">Please sign up first to verify your email.</p>
          <Link 
            href="/"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Go to Signup
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <Shield className="h-12 w-12 text-blue-600" />
        </div>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Verify Your Email
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          We&apos;ve sent a verification code to
        </p>
        <p className="text-center text-sm font-medium text-blue-600">
          {email}
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <form onSubmit={handleSubmit(verifyOTP)} className="space-y-6">
            <div>
              <label htmlFor="otpCode" className="block text-sm font-medium text-gray-700">
                Enter 6-digit verification code
              </label>
              <div className="mt-1 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  {...register('otpCode')}
                  type="text"
                  maxLength={6}
                  placeholder="123456"
                  className="appearance-none block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-center text-lg tracking-widest"
                />
              </div>
              {errors.otpCode && (
                <p className="mt-1 text-sm text-red-600">{errors.otpCode.message}</p>
              )}
            </div>

            <div className="text-center">
              {countdown > 0 ? (
                <p className="text-sm text-gray-600">
                  Code expires in <span className="font-medium text-orange-600">{formatCountdown(countdown)}</span>
                </p>
              ) : (
                <p className="text-sm text-red-600">Code expired</p>
              )}
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Verifying...
                  </>
                ) : (
                  'Verify Email'
                )}
              </button>
            </div>

            <div className="text-center">
              <button
                type="button"
                onClick={resendOTP}
                disabled={isLoading || countdown > 0}
                className="text-sm text-blue-600 hover:text-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Didn&apos;t receive the code? Resend
              </button>
            </div>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Need help?</span>
              </div>
            </div>

            <div className="mt-6 text-center">
              <Link
                href="/"
                className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="h-4 w-4 mr-1" />
                Back to Login
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Success overlay */}
      {user?.is_email_verified && (
        <div className="fixed inset-0 bg-green-50 bg-opacity-95 flex items-center justify-center z-50">
          <div className="text-center">
            <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-green-900 mb-2">Email Verified!</h3>
            <p className="text-green-700">Redirecting to dashboard...</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          <span className="text-gray-600">Loading...</span>
        </div>
      </div>
    }>
      <VerifyEmailContent />
    </Suspense>
  );
}
