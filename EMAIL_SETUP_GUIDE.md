# 📧 Email Setup Guide

## Current Status
✅ **OTP Generation**: Working  
✅ **Database Storage**: Working  
✅ **OTP Verification**: Working  
❌ **Real Email Sending**: Currently using mock (console output)

## 🔧 Setting Up Real Email Sending

### Option 1: Gmail SMTP (Recommended - Free)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. **Add to your `.env` file**:
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_16_character_app_password
   SENDER_NAME=User Management System
   ```

### Option 2: Outlook/Hotmail SMTP

Add to your `.env` file:
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SENDER_EMAIL=your_email@outlook.com
SENDER_PASSWORD=your_password
SENDER_NAME=User Management System
```

### Option 3: Custom SMTP Server

Add to your `.env` file:
```env
SMTP_SERVER=your_smtp_server.com
SMTP_PORT=587
SENDER_EMAIL=your_email@yourdomain.com
SENDER_PASSWORD=your_password
SENDER_NAME=User Management System
```

## 🧪 Testing Email Functionality

### Current Testing Method
OTPs are currently printed to the console. Check the backend logs:
```bash
tail -f backend/server.log
```

### Test OTP Generation
```bash
curl -X POST http://localhost:8000/email/send-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

### Test OTP Verification
```bash
curl -X POST http://localhost:8000/email/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "otp_code": "123456"}'
```

## 📱 Frontend Testing

1. **Sign up** with a new account
2. **Check console** for OTP code
3. **Enter OTP** in the verification page
4. **Verify** email verification works

## 🔄 After Setting Up Real Email

1. **Restart the backend server**
2. **Test signup flow** with a real email address
3. **Check email inbox** for OTP
4. **Verify** the complete flow works

## 🛠️ Troubleshooting

### Gmail Issues
- Make sure 2FA is enabled
- Use App Password, not regular password
- Check if "Less secure app access" is enabled (if not using App Password)

### SMTP Connection Issues
- Verify SMTP server and port
- Check firewall settings
- Ensure credentials are correct

### Email Not Received
- Check spam folder
- Verify email address is correct
- Check SMTP server logs

## 📋 Environment Variables

Add these to your `backend/.env` file:

```env
# Required for Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Optional for real email (if not provided, uses console output)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
SENDER_NAME=User Management System
```

## 🎯 Next Steps

1. **Choose email provider** (Gmail recommended)
2. **Set up credentials** in `.env` file
3. **Restart backend server**
4. **Test complete flow** with real email
5. **Verify emails are received** and OTP verification works
