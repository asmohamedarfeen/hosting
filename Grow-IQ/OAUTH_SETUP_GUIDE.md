# 🔐 OAuth Setup Guide for CareerConnect

## 📋 **Prerequisites**
- Google Cloud Console account
- CareerConnect application running locally
- Python environment with required packages

## 🚀 **Step 1: Google Cloud Console Setup**

### 1.1 Create/Select Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable billing (required for OAuth)

### 1.2 Enable APIs
1. Go to **APIs & Services** → **Library**
2. Search and enable these APIs:
   - **Google+ API**
   - **Google OAuth2 API**
   - **Google Identity API**

### 1.3 Configure OAuth Consent Screen
1. Go to **APIs & Services** → **OAuth consent screen**
2. **User Type**: External (for public access)
3. **App Information**:
   - App name: `CareerConnect`
   - User support email: Your email
   - Developer contact information: Your email
4. **Scopes**: Add these scopes:
   - `openid`
   - `email`
   - `profile`
5. **Test Users**: Add your email for testing

### 1.4 Create OAuth Client ID
1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth 2.0 Client IDs**
3. **Application type**: Web application
4. **Name**: `CareerConnect Web Client`
5. **Authorized JavaScript origins**:
   ```
   http://localhost:8000
   http://127.0.0.1:8000
   ```
6. **Authorized redirect URIs**:
   ```
   http://localhost:8000/auth/google/callback
   http://127.0.0.1:8000/auth/google/callback
   ```

### 1.5 Save Your Credentials
You'll get:
- **Client ID**: `123456789-abcdef.apps.googleusercontent.com`
- **Client Secret**: `GOCSPX-abcdefghijklmnop`

## ⚙️ **Step 2: Configure CareerConnect**

### 2.1 Create Environment File
Create a `.env` file in your project root:

```bash
# .env
ENVIRONMENT=development
GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
SESSION_SECRET_KEY=your-super-secret-key-change-in-production
SECURE_COOKIES=false
```

### 2.2 Install Required Packages
```bash
pip install requests
# or if using uv
uv add requests
```

### 2.3 Update Database
The OAuth system adds a `google_id` field to the User model. If you have existing data, you may need to run database migrations.

## 🧪 **Step 3: Test OAuth Integration**

### 3.1 Start the Server
```bash
python start.py
```

### 3.2 Test OAuth Flow
1. Navigate to `http://localhost:8000/login`
2. Click "Continue with Google"
3. Complete Google OAuth flow
4. Verify successful login and redirect

### 3.3 Check OAuth Endpoints
Test these endpoints:
- `GET /auth/google` - Initiates OAuth
- `GET /auth/google/callback` - OAuth callback
- `GET /auth/status` - Check auth status
- `GET /auth/logout` - Logout

## 🔧 **Step 4: Production Configuration**

### 4.1 Update Environment Variables
```bash
# Production .env
ENVIRONMENT=production
GOOGLE_CLIENT_ID=your-production-client-id
GOOGLE_CLIENT_SECRET=your-production-client-secret
GOOGLE_REDIRECT_URI=https://yourdomain.com/auth/google/callback
SESSION_SECRET_KEY=your-production-secret-key
SECURE_COOKIES=true
SAME_SITE_COOKIES=strict
```

### 4.2 Update Google OAuth Settings
1. Go to Google Cloud Console
2. Update **Authorized JavaScript origins**:
   ```
   https://yourdomain.com
   ```
3. Update **Authorized redirect URIs**:
   ```
   https://yourdomain.com/auth/google/callback
   ```

### 4.3 Security Considerations
- Use HTTPS in production
- Set `SECURE_COOKIES=true`
- Use strong `SESSION_SECRET_KEY`
- Consider using Redis for OAuth state storage
- Implement rate limiting

## 🐛 **Troubleshooting**

### Common Issues

#### 1. "Invalid redirect_uri" Error
- Verify redirect URI matches exactly in Google Console
- Check for trailing slashes
- Ensure protocol (http/https) matches

#### 2. "Invalid client" Error
- Verify Client ID and Secret are correct
- Check if OAuth consent screen is configured
- Ensure APIs are enabled

#### 3. "State parameter expired" Error
- OAuth state tokens expire after 5 minutes
- Check system clock synchronization
- Verify no proxy/cache interference

#### 4. Database Errors
- Ensure `google_id` field exists in User table
- Check database permissions
- Verify SQLite file is writable

### Debug Mode
Enable debug logging:
```python
# In your app.py or config.py
logging.basicConfig(level=logging.DEBUG)
```

## 📚 **API Reference**

### OAuth Endpoints

#### `GET /auth/google`
- **Purpose**: Initiate Google OAuth login
- **Parameters**: `redirect` (optional) - redirect after login
- **Response**: Redirects to Google OAuth

#### `GET /auth/google/callback`
- **Purpose**: Handle OAuth callback
- **Parameters**: `code`, `state`, `error` (optional)
- **Response**: Redirects to dashboard or specified page

#### `GET /auth/status`
- **Purpose**: Check authentication status
- **Response**: JSON with user info and auth status

#### `GET /auth/logout`
- **Purpose**: Logout user
- **Response**: Redirects to login page

#### `GET /auth/error`
- **Purpose**: Display OAuth errors
- **Parameters**: `error`, `error_description` (optional)
- **Response**: HTML error page

## 🔮 **Future Enhancements**

### Additional OAuth Providers
- **LinkedIn OAuth**: Professional networking integration
- **GitHub OAuth**: Developer community integration
- **Microsoft OAuth**: Enterprise integration
- **Apple OAuth**: iOS ecosystem integration

### Advanced Features
- **OAuth State Persistence**: Redis/database storage
- **Refresh Token Handling**: Automatic token renewal
- **Multi-Provider Accounts**: Link multiple OAuth accounts
- **OAuth Analytics**: Track login patterns and success rates

## 📞 **Support**

### Getting Help
1. Check this guide first
2. Review Google OAuth documentation
3. Check CareerConnect logs
4. Verify environment configuration

### Useful Links
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)
- [FastAPI OAuth Documentation](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Maintainer**: CareerConnect Development Team
