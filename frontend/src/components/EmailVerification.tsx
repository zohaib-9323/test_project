/**
 * Email Verification Component
 *
 * This component handles the email verification process using OTP codes:
 * - Displays verification status
 * - Allows sending OTP codes
 * - Handles OTP verification
 * - Shows countdown timer for OTP expiry
 * - Provides resend functionality
 *
 * Used in profile pages and signup flows for email verification.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { emailAPI, OTPResponse, EmailVerificationResponse } from '@/lib/api';
import toast from 'react-hot-toast';

// Validation schema for OTP input
const otpSchema = z.object({
  otpCode: z
    .string()
    .min(6, 'OTP must be 6 digits')
    .max(6, 'OTP must be 6 digits')
    .regex(/^\d{6}$/, 'OTP must contain only numbers'),
});

type OTPFormData = z.infer<typeof otpSchema>;

interface EmailVerificationProps {
  email: string;
  isVerified: boolean;
  onVerificationSuccess: () => void;
  isAuthenticated?: boolean; // Whether user is logged in
}

export default function EmailVerification({
  email,
  isVerified,
  onVerificationSuccess,
  isAuthenticated = false,
}: EmailVerificationProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [otpSent, setOtpSent] = useState(false);
  const [countdown, setCountdown] = useState(0);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<OTPFormData>({
    resolver: zodResolver(otpSchema),
  });

  // Countdown timer effect
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (countdown > 0) {
      interval = setInterval(() => {
        setCountdown(prev => prev - 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [countdown]);

  // Format countdown display
  const formatCountdown = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Send OTP function
  const sendOTP = async () => {
    setIsLoading(true);
    try {
      const response = await (isAuthenticated
        ? emailAPI.sendOTPAuthenticated()
        : emailAPI.sendOTP(email));

      const data: OTPResponse = response.data;

      if (data.success) {
        setOtpSent(true);
        setCountdown(data.expires_in_minutes * 60);
        toast.success(data.message);
      } else {
        toast.error('Failed to send OTP');
      }
    } catch (error: unknown) {
      const errorMessage =
        (error as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || 'Failed to send OTP';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Verify OTP function
  const verifyOTP = async (data: OTPFormData) => {
    setIsLoading(true);
    try {
      const response = await (isAuthenticated
        ? emailAPI.verifyOTPAuthenticated(data.otpCode)
        : emailAPI.verifyOTP(email, data.otpCode));

      const result: EmailVerificationResponse = response.data;

      if (result.success) {
        toast.success(result.message);
        setOtpSent(false);
        setCountdown(0);
        reset();
        onVerificationSuccess();
      } else {
        toast.error('OTP verification failed');
      }
    } catch (error: unknown) {
      const errorMessage =
        (error as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || 'OTP verification failed';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Resend OTP function
  const resendOTP = async () => {
    setIsLoading(true);
    try {
      const response = await (isAuthenticated
        ? emailAPI.sendOTPAuthenticated()
        : emailAPI.resendOTP(email));

      const data: OTPResponse = response.data;

      if (data.success) {
        setCountdown(data.expires_in_minutes * 60);
        toast.success('OTP resent successfully');
      } else {
        toast.error('Failed to resend OTP');
      }
    } catch (error: unknown) {
      const errorMessage =
        (error as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || 'Failed to resend OTP';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // If email is already verified, show success status
  if (isVerified) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <svg
              className="h-5 w-5 text-green-400"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-green-800">
              Email Verified
            </h3>
            <div className="mt-1 text-sm text-green-700">
              <p>Your email address has been verified successfully.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg
            className="h-5 w-5 text-yellow-400"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-yellow-800">
            Email Verification Required
          </h3>
          <div className="mt-1 text-sm text-yellow-700">
            <p>Please verify your email address to access all features.</p>
            <p className="mt-1 font-medium">Email: {email}</p>
          </div>

          {!otpSent ? (
            <div className="mt-4">
              <button
                onClick={sendOTP}
                disabled={isLoading}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-yellow-600 hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <svg
                      className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    Sending...
                  </>
                ) : (
                  'Send Verification Code'
                )}
              </button>
            </div>
          ) : (
            <div className="mt-4">
              <form onSubmit={handleSubmit(verifyOTP)} className="space-y-4">
                <div>
                  <label
                    htmlFor="otpCode"
                    className="block text-sm font-medium text-yellow-800"
                  >
                    Enter 6-digit verification code
                  </label>
                  <div className="mt-1">
                    <input
                      {...register('otpCode')}
                      type="text"
                      maxLength={6}
                      placeholder="123456"
                      className="block w-full px-3 py-2 border border-yellow-300 rounded-md shadow-sm placeholder-yellow-400 focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm"
                    />
                    {errors.otpCode && (
                      <p className="mt-1 text-sm text-red-600">
                        {errors.otpCode.message}
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="text-sm text-yellow-700">
                    {countdown > 0 ? (
                      <span>Code expires in {formatCountdown(countdown)}</span>
                    ) : (
                      <span className="text-red-600">Code expired</span>
                    )}
                  </div>

                  <div className="flex space-x-2">
                    <button
                      type="button"
                      onClick={resendOTP}
                      disabled={isLoading || countdown > 0}
                      className="text-sm text-yellow-600 hover:text-yellow-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Resend Code
                    </button>

                    <button
                      type="submit"
                      disabled={isLoading}
                      className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-yellow-600 hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isLoading ? (
                        <>
                          <svg
                            className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none"
                            viewBox="0 0 24 24"
                          >
                            <circle
                              className="opacity-25"
                              cx="12"
                              cy="12"
                              r="10"
                              stroke="currentColor"
                              strokeWidth="4"
                            ></circle>
                            <path
                              className="opacity-75"
                              fill="currentColor"
                              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                            ></path>
                          </svg>
                          Verifying...
                        </>
                      ) : (
                        'Verify Code'
                      )}
                    </button>
                  </div>
                </div>
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
