# Grow-IQ Render Deployment Guide

This guide will walk you through deploying your Grow-IQ application to Render.com step by step.

## 📋 Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com) (free tier available)
2. **GitHub/GitLab/Bitbucket Repository**: Your code should be in a Git repository
3. **PostgreSQL Database**: Render provides managed PostgreSQL (or use external service)
4. **Environment Variables**: List of all required environment variables (see below)

---

## 🏗️ Architecture Overview

Your application consists of:
- **Backend**: FastAPI (Python) - Main API server
- **Frontend**: React/Vite (TypeScript) - Optional separate deployment
- **Database**: PostgreSQL (recommended for production) or SQLite (development only)

---

## 📝 Step-by-Step Deployment

### **Step 1: Prepare Your Repository**

1. **Ensure all files are committed and pushed to your Git repository**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Verify these files exist in your repository:**
   - `requirements.txt` (or `requirements_production.txt`)
   - `start.py` or `working_start.py` (entry point)
   - `config.py`
   - `app.py`

---

### **Step 2: Create PostgreSQL Database on Render**

1. **Log in to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → Select **"PostgreSQL"**
3. **Configure Database:**
   - **Name**: `grow-iq-db` (or your preferred name)
   - **Database**: `growiq` (or your preferred name)
   - **User**: Auto-generated (or custom)
   - **Region**: Choose closest to your users
   - **PostgreSQL Version**: 15 or 16 (recommended)
   - **Plan**: Free tier available (or paid for production)
4. **Click "Create Database"**
5. **Copy the Internal Database URL** (you'll need this later)
   - Format: `postgresql://user:password@host:port/database`

---

### **Step 3: Deploy Backend Web Service**

1. **In Render Dashboard, click "New +"** → Select **"Web Service"**

2. **Connect Repository:**
   - Connect your GitHub/GitLab/Bitbucket account
   - Select your repository
   - Choose the branch (usually `main` or `master`)

3. **Configure Service:**
   - **Name**: `grow-iq-backend` (or your preferred name)
   - **Region**: Same as database (for lower latency)
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave empty (or `Grow-IQ` if your app is in a subdirectory)
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     uvicorn app:app --host 0.0.0.0 --port $PORT
     ```
     OR if you prefer using your start script:
     ```bash
     python working_start.py
     ```
     (Note: You may need to modify `working_start.py` to use `$PORT` environment variable)

4. **Environment Variables** (Click "Advanced" → "Add Environment Variable"):
   
   **Required Variables:**
   ```
   ENVIRONMENT=production
   DEBUG=false
   SECRET_KEY=your-super-secret-key-here-change-this
   DATABASE_URL=<paste-internal-database-url-from-step-2>
   HOST=0.0.0.0
   PORT=$PORT
   WORKERS=2
   ```
   
   **Optional but Recommended:**
   ```
   LOG_LEVEL=INFO
   CORS_ORIGINS=https://your-frontend-domain.onrender.com,https://your-custom-domain.com
   ALLOWED_HOSTS=your-backend.onrender.com,your-custom-domain.com
   API_RATE_LIMIT=100
   MAX_FILE_SIZE=16777216
   UPLOAD_FOLDER=./static/uploads
   ```
   
   **OAuth (if using Google OAuth):**
   ```
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   GOOGLE_REDIRECT_URI=https://your-backend.onrender.com/auth/google/callback
   ```
   
   **AI Services (if using Gemini):**
   ```
   GEMINI_API_KEY=your-gemini-api-key
   ```
   
   **Azure (if using Azure Storage):**
   ```
   AZURE_STORAGE_CONNECTION_STRING=your-azure-connection-string
   AZURE_CONTAINER_NAME=media
   ```

5. **Click "Create Web Service"**

6. **Wait for Deployment**: Render will build and deploy your application (5-10 minutes)

---

### **Step 4: Configure Database Migrations**

After the first deployment, you may need to run database migrations:

1. **Option A: Use Render Shell** (Recommended)
   - Go to your web service
   - Click "Shell" tab
   - Run:
     ```bash
     python -c "from database_enhanced import init_database; init_database()"
     ```
   OR if you have Alembic:
     ```bash
     alembic upgrade head
     ```

2. **Option B: Add to Startup Script**
   - Modify your startup script to run migrations automatically
   - See `render_start.py` example in this guide

---

### **Step 5: Deploy Frontend (Optional - Separate Service)**

If you want to deploy the frontend separately:

1. **Create New Web Service** → **"Static Site"** (if frontend is static)
   OR **"Web Service"** (if using Node.js server)

2. **For Static Site:**
   - **Build Command**: 
     ```bash
     cd fronted && npm install && npm run build
     ```
   - **Publish Directory**: `fronted/dist/public`

3. **For Web Service (Node.js):**
   - **Build Command**: 
     ```bash
     cd fronted && npm install && npm run build
     ```
   - **Start Command**: 
     ```bash
     cd fronted && npm start
     ```
   - **Environment Variables**:
     ```
     NODE_ENV=production
     API_URL=https://your-backend.onrender.com
     ```

---

### **Step 6: Configure Custom Domain (Optional)**

1. **In your Web Service settings** → **"Custom Domains"**
2. **Add your domain** (e.g., `api.yourdomain.com`)
3. **Update DNS records** as instructed by Render
4. **Update CORS_ORIGINS** environment variable to include your custom domain

---

### **Step 7: Verify Deployment**

1. **Check Health Endpoint**: 
   ```
   https://your-backend.onrender.com/health
   ```

2. **Check API Docs**: 
   ```
   https://your-backend.onrender.com/docs
   ```

3. **Test Main Routes**: 
   ```
   https://your-backend.onrender.com/
   ```

---

## 🔧 Troubleshooting

### **Issue: Application fails to start**

**Solutions:**
- Check Render logs: Go to your service → "Logs" tab
- Verify `PORT` environment variable is set to `$PORT`
- Ensure `requirements.txt` includes all dependencies
- Check Python version compatibility (Render uses Python 3.11+)

### **Issue: Database connection errors**

**Solutions:**
- Verify `DATABASE_URL` uses the **Internal Database URL** (not external)
- Check database is running: Go to database service → "Status"
- Ensure `psycopg2-binary` is in `requirements.txt`
- Test connection using Render Shell

### **Issue: Static files not loading**

**Solutions:**
- Verify `UPLOAD_FOLDER` directory exists
- Check file permissions
- Consider using external storage (Azure Blob, S3) for production

### **Issue: CORS errors**

**Solutions:**
- Update `CORS_ORIGINS` to include your frontend URL
- Verify frontend is making requests to correct backend URL
- Check `ALLOWED_HOSTS` includes your backend domain

### **Issue: Build timeout**

**Solutions:**
- Optimize `requirements.txt` (remove unused packages)
- Use `requirements_production.txt` with minimal dependencies
- Check for heavy dependencies that might slow build

---

## 📦 Required Files Checklist

Ensure these files are in your repository:

- ✅ `requirements.txt` or `requirements_production.txt`
- ✅ `app.py` (main FastAPI application)
- ✅ `config.py` (configuration)
- ✅ `start.py` or `working_start.py` (entry point)
- ✅ `database.py` or `database_enhanced.py`
- ✅ `models.py`
- ✅ `.gitignore` (excludes sensitive files)

---

## 🔐 Security Best Practices

1. **Never commit `.env` files** - Use Render environment variables
2. **Use strong SECRET_KEY** - Generate with:
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   ```
3. **Enable HTTPS** - Render provides this automatically
4. **Use Internal Database URL** - More secure than external
5. **Set DEBUG=false** in production
6. **Limit CORS_ORIGINS** - Only include trusted domains

---

## 💰 Cost Considerations

**Free Tier Limits:**
- Web Services: Sleep after 15 minutes of inactivity
- PostgreSQL: 90 days free trial, then $7/month
- Bandwidth: 100GB/month free

**Paid Plans:**
- Starter: $7/month (always-on, better performance)
- Professional: $25/month (auto-scaling, better resources)

---

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL on Render](https://render.com/docs/databases)

---

## 🆘 Support

If you encounter issues:
1. Check Render logs first
2. Review this guide's troubleshooting section
3. Check Render status page: https://status.render.com
4. Contact Render support: support@render.com

---

## ✅ Post-Deployment Checklist

- [ ] Backend is accessible at provided URL
- [ ] Health endpoint returns 200 OK
- [ ] Database connection successful
- [ ] Environment variables configured
- [ ] CORS configured for frontend
- [ ] Static file uploads working (or using external storage)
- [ ] OAuth callbacks updated (if using OAuth)
- [ ] Custom domain configured (if applicable)
- [ ] Monitoring/logging set up
- [ ] Backup strategy in place

---

**Last Updated**: 2025-01-27
**Version**: 1.0
