from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, validator


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    COMPANY = "company"


class UserBase(BaseModel):
    name: str
    email: EmailStr

    @validator("name")
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError("Name must be at least 2 characters long")
        return v.strip()


class UserCreate(UserBase):
    password: str
    role: Optional[UserRole] = UserRole.USER  # Default role is user

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None

    @validator("name")
    def validate_name(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError("Name must be at least 2 characters long")
        return v.strip() if v else v


class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    is_email_verified: bool = False

    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Email Verification Models
class EmailVerificationRequest(BaseModel):
    email: EmailStr


class EmailVerificationVerify(BaseModel):
    email: EmailStr
    otp_code: str

    @validator("otp_code")
    def validate_otp_code(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError("OTP code must be exactly 6 digits")
        return v


class EmailVerificationResponse(BaseModel):
    message: str
    success: bool


class OTPResponse(BaseModel):
    message: str
    success: bool
    expires_in_minutes: int = 10
    otp_code: Optional[str] = None  # Include OTP for testing purposes
