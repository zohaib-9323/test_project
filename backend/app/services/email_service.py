"""
Email Service Module

This module handles email-related operations including:
- OTP generation and validation
- Email verification workflow
- OTP storage and cleanup

The service manages the email verification process using OTP codes.
"""

import random
import string
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from app.config.database import db_config
from app.models.user import EmailVerificationResponse, OTPResponse
from app.services.real_email_service import real_email_service


class EmailService:
    def __init__(self):
        self.db = db_config.get_client()
        self.otp_table = "email_otps"
        self.users_table = "users"
        self.otp_expiry_minutes = 10  # OTP expires in 10 minutes

    def generate_otp(self) -> str:
        """Generate a 6-digit OTP code."""
        return "".join(random.choices(string.digits, k=6))

    async def send_otp(self, email: str) -> OTPResponse:
        """
        Send OTP to email address.

        Args:
            email: Email address to send OTP to

        Returns:
            OTPResponse: Response with success status and expiry info
        """
        try:
            # Check if user exists
            user_result = (
                self.db.table(self.users_table)
                .select("id, is_email_verified")
                .eq("email", email)
                .execute()
            )

            if not user_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            user = user_result.data[0]

            # Check if email is already verified
            if user.get("is_email_verified", False):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email is already verified",
                )

            # Generate OTP
            otp_code = self.generate_otp()
            expires_at = datetime.now(timezone.utc) + timedelta(
                minutes=self.otp_expiry_minutes
            )

            # Invalidate any existing OTPs for this email
            self.db.table(self.otp_table).update({"is_used": True}).eq(
                "email", email
            ).execute()

            # Store new OTP
            otp_data = {
                "email": email,
                "otp_code": otp_code,
                "expires_at": expires_at.isoformat(),
                "is_used": False,
            }

            result = self.db.table(self.otp_table).insert(otp_data).execute()

            if result.data:
                # Send OTP via real email service
                await real_email_service.send_otp_email(
                    email, otp_code, self.otp_expiry_minutes
                )

                # Always return OTP in response for testing purposes
                return OTPResponse(
                    message=f"OTP sent to {email}. Check your email. OTP: {otp_code}",
                    success=True,
                    expires_in_minutes=self.otp_expiry_minutes,
                    otp_code=otp_code,  # Include OTP in response for testing
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send OTP",
                )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error sending OTP: {str(e)}",
            )

    async def verify_otp(self, email: str, otp_code: str) -> EmailVerificationResponse:
        """
        Verify OTP code for email verification.

        Args:
            email: Email address to verify
            otp_code: 6-digit OTP code

        Returns:
            EmailVerificationResponse: Response with verification status
        """
        try:
            # Find valid OTP
            otp_result = (
                self.db.table(self.otp_table)
                .select("*")
                .eq("email", email)
                .eq("otp_code", otp_code)
                .eq("is_used", False)
                .execute()
            )

            if not otp_result.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired OTP",
                )

            otp_record = otp_result.data[0]
            expires_at = datetime.fromisoformat(
                otp_record["expires_at"].replace("Z", "+00:00")
            )

            # Check if OTP is expired
            current_time = datetime.now(timezone.utc)
            if current_time > expires_at:
                # Mark as used to prevent reuse
                self.db.table(self.otp_table).update({"is_used": True}).eq(
                    "id", otp_record["id"]
                ).execute()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired"
                )

            # Mark OTP as used
            self.db.table(self.otp_table).update({"is_used": True}).eq(
                "id", otp_record["id"]
            ).execute()

            # Update user email verification status
            user_result = (
                self.db.table(self.users_table)
                .update(
                    {
                        "is_email_verified": True,
                        "email_verification_token": None,
                        "email_verification_expires_at": None,
                    }
                )
                .eq("email", email)
                .execute()
            )

            if user_result.data:
                return EmailVerificationResponse(
                    message="Email verified successfully", success=True
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update email verification status",
                )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error verifying OTP: {str(e)}",
            )

    async def resend_otp(self, email: str) -> OTPResponse:
        """
        Resend OTP to email address.

        Args:
            email: Email address to resend OTP to

        Returns:
            OTPResponse: Response with success status
        """
        return await self.send_otp(email)

    async def cleanup_expired_otps(self) -> int:
        """
        Clean up expired OTPs from database.

        Returns:
            int: Number of OTPs cleaned up
        """
        try:
            # Mark expired OTPs as used
            result = (
                self.db.table(self.otp_table)
                .update({"is_used": True})
                .lt("expires_at", datetime.now(timezone.utc).isoformat())
                .execute()
            )
            return len(result.data) if result.data else 0
        except Exception as e:
            print(f"Error cleaning up expired OTPs: {str(e)}")
            return 0


# Global email service instance
email_service = EmailService()
