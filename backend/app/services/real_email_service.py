"""
Real Email Service Module

This module provides real email sending functionality using SMTP.
Supports Gmail, Outlook, and other SMTP providers.
"""

import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class RealEmailService:
    def __init__(self):
        # Email configuration from environment variables
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")  # App password for Gmail
        self.sender_name = os.getenv("SENDER_NAME", "User Management System")

        if not self.sender_email or not self.sender_password:
            print("⚠️  Email credentials not configured. Using mock email service.")
            self.enabled = False
        else:
            self.enabled = True

    async def send_otp_email(
        self, email: str, otp_code: str, expires_in_minutes: int = 10
    ) -> bool:
        """
        Send OTP email to user.

        Args:
            email: Recipient email address
            otp_code: 6-digit OTP code
            expires_in_minutes: OTP expiry time in minutes

        Returns:
            bool: True if email sent successfully
        """
        if not self.enabled:
            # Fallback to console output
            print(
                f"🔐 OTP for {email}: {otp_code} (expires in {expires_in_minutes} minutes)"
            )
            return True

        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"Email Verification Code - {self.sender_name}"
            message["From"] = f"{self.sender_name} <{self.sender_email}>"
            message["To"] = email

            # Create HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Email Verification</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .container {{
                        background-color: #f9f9f9;
                        padding: 30px;
                        border-radius: 10px;
                        border: 1px solid #ddd;
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    .logo {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #2563eb;
                        margin-bottom: 10px;
                    }}
                    .otp-code {{
                        background-color: #2563eb;
                        color: white;
                        font-size: 32px;
                        font-weight: bold;
                        text-align: center;
                        padding: 20px;
                        border-radius: 8px;
                        letter-spacing: 5px;
                        margin: 20px 0;
                    }}
                    .warning {{
                        background-color: #fef3c7;
                        border: 1px solid #f59e0b;
                        color: #92400e;
                        padding: 15px;
                        border-radius: 8px;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        color: #666;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">🔐 User Management System</div>
                        <h1>Email Verification</h1>
                    </div>

                    <p>Hello,</p>

                    <p>You have requested to verify your email address. Please use the following verification code:</p>

                    <div class="otp-code">{otp_code}</div>

                    <div class="warning">
                        <strong>⚠️ Important:</strong>
                        <ul>
                            <li>This code will expire in {expires_in_minutes} minutes</li>
                            <li>Do not share this code with anyone</li>
                            <li>If you didn't request this, please ignore this email</li>
                        </ul>
                    </div>

                    <p>If you have any questions, please contact our support team.</p>

                    <div class="footer">
                        <p>This is an automated message. Please do not reply to this email.</p>
                        <p>&copy; 2024 User Management System. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Create plain text content
            text_content = f"""
            Email Verification Code

            Hello,

            You have requested to verify your email address. Please use the following verification code:

            {otp_code}

            Important:
            - This code will expire in {expires_in_minutes} minutes
            - Do not share this code with anyone
            - If you didn't request this, please ignore this email

            If you have any questions, please contact our support team.

            This is an automated message. Please do not reply to this email.
            © 2024 User Management System. All rights reserved.
            """

            # Attach parts
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")

            message.attach(text_part)
            message.attach(html_part)

            # Create secure connection and send email
            context = ssl.create_default_context()

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, email, message.as_string())

            print(f"✅ OTP email sent successfully to {email}")
            return True

        except Exception as e:
            print(f"❌ Failed to send email to {email}: {str(e)}")
            # Fallback to console output
            print(
                f"🔐 OTP for {email}: {otp_code} (expires in {expires_in_minutes} minutes)"
            )
            return False


# Global email service instance
real_email_service = RealEmailService()
