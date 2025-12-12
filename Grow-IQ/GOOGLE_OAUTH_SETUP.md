# Google OAuth Setup Guide for Qrow IQ

## 🚀 Quick Setup

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google+ API

### 2. Configure OAuth Consent Screen
1. Go to **APIs & Services** > **OAuth consent screen**
2. Choose **External** user type
3. Fill in required information:
   - App name: `Qrow IQ`
   - User support email: Your email
   - Developer contact information: Your email
4. Add scopes: `email`, `profile`, `openid`
5. Add test users (your email)

### 3. Create OAuth Credentials
1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth 2.0 Client IDs**
3. Choose **Web application**
4. Set authorized redirect URIs:
   - `http://localhost:8000/auth/google/callback` (development)
   - `https://yourdomain.com/auth/google/callback` (production)

### 4. Set Environment Variables
Create a `.env` file in your project root:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# App Settings
DEBUG=true
ENVIRONMENT=development
SECRET_KEY=your_secret_key_here
```

### 5. Install Dependencies
```bash
pip install requests python-dotenv
```

## 🔧 How It Works

### OAuth Flow:
1. **User clicks "Continue with Google"**
2. **Redirect to Google** for authentication
3. **Google returns authorization code**
4. **Exchange code for access token**
5. **Get user info from Google**
6. **Create/update user account**
7. **Create session and redirect**

### Routes:
- `GET /auth/google` - Initiate OAuth
- `GET /auth/google/callback` - Handle callback

## 🎯 Features

✅ **Secure OAuth flow** with state parameter  
✅ **Automatic user creation** for new Google users  
✅ **Profile sync** with Google account data  
✅ **Session management** after OAuth login  
✅ **Error handling** for OAuth failures  

## 🚨 Security Notes

- **State parameter** prevents CSRF attacks
- **HTTPS required** in production
- **Secure cookies** in production
- **Rate limiting** on OAuth endpoints

## 🐛 Troubleshooting

### Common Issues:
1. **"Invalid redirect URI"** - Check redirect URI in Google Console
2. **"OAuth consent screen not configured"** - Complete consent screen setup
3. **"API not enabled"** - Enable Google+ API in Cloud Console

### Debug Mode:
Set `DEBUG=true` in environment for detailed logging.

## 📱 Testing

1. Start your application
2. Go to login page
3. Click "Continue with Google"
4. Complete Google authentication
5. Should redirect to dashboard

## 🔄 Production Deployment

1. Update redirect URIs in Google Console
2. Set `ENVIRONMENT=production`
3. Use HTTPS URLs
4. Set secure session cookies
5. Configure proper domain in Google Console
