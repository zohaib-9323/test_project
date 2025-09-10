"""
Email Verification Routes Module

This module handles all email verification-related API endpoints including:
- Send OTP for email verification
- Verify OTP code
- Resend OTP code

The routes handle the email verification workflow using OTP codes.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.middleware.auth import get_current_active_user
from app.models.user import (
    EmailVerificationRequest,
    EmailVerificationResponse,
    EmailVerificationVerify,
    OTPResponse,
    UserInDB,
)
from app.services.email_service import email_service

# Create router for email verification endpoints
router = APIRouter(prefix="/email", tags=["email verification"])


@router.post("/send-otp", response_model=OTPResponse)
async def send_otp(request: EmailVerificationRequest):
    """
    Send OTP code to email address for verification.

    Args:
        request: EmailVerificationRequest containing email address

    Returns:
        OTPResponse: Response with success status and expiry information

    Raises:
        HTTPException: 404 if user not found, 400 if email already verified, 500 for server errors
    """
    try:
        return await email_service.send_otp(request.email)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while sending OTP: {str(e)}",
        )


@router.post("/verify-otp", response_model=EmailVerificationResponse)
async def verify_otp(request: EmailVerificationVerify):
    """
    Verify OTP code for email verification.

    Args:
        request: EmailVerificationVerify containing email and OTP code

    Returns:
        EmailVerificationResponse: Response with verification status

    Raises:
        HTTPException: 400 for invalid/expired OTP, 500 for server errors
    """
    try:
        return await email_service.verify_otp(request.email, request.otp_code)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while verifying OTP: {str(e)}",
        )


@router.post("/resend-otp", response_model=OTPResponse)
async def resend_otp(request: EmailVerificationRequest):
    """
    Resend OTP code to email address.

    Args:
        request: EmailVerificationRequest containing email address

    Returns:
        OTPResponse: Response with success status and expiry information

    Raises:
        HTTPException: 404 if user not found, 400 if email already verified, 500 for server errors
    """
    try:
        return await email_service.resend_otp(request.email)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while resending OTP: {str(e)}",
        )


@router.post("/send-otp-authenticated", response_model=OTPResponse)
async def send_otp_authenticated(
    current_user: UserInDB = Depends(get_current_active_user),
):
    """
    Send OTP code to current authenticated user's email.

    Args:
        current_user: Current authenticated user from JWT token

    Returns:
        OTPResponse: Response with success status and expiry information

    Raises:
        HTTPException: 400 if email already verified, 500 for server errors
    """
    try:
        return await email_service.send_otp(current_user.email)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while sending OTP: {str(e)}",
        )


@router.post("/verify-otp-authenticated", response_model=EmailVerificationResponse)
async def verify_otp_authenticated(
    otp_code: str, current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Verify OTP code for current authenticated user's email.

    Args:
        otp_code: 6-digit OTP code
        current_user: Current authenticated user from JWT token

    Returns:
        EmailVerificationResponse: Response with verification status

    Raises:
        HTTPException: 400 for invalid/expired OTP, 500 for server errors
    """
    try:
        return await email_service.verify_otp(current_user.email, otp_code)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while verifying OTP: {str(e)}",
        )
