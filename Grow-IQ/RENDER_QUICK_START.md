# 🚀 Render Quick Start Guide

## TL;DR - Deploy in 5 Minutes

### 1. Create PostgreSQL Database
- Render Dashboard → "New +" → "PostgreSQL"
- Name: `grow-iq-db`
- Copy **Internal Database URL**

### 2. Create Web Service
- Render Dashboard → "New +" → "Web Service"
- Connect your Git repository
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

### 3. Set Environment Variables
```
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<generate-strong-key>
DATABASE_URL=<internal-db-url-from-step-1>
HOST=0.0.0.0
PORT=$PORT
```

### 4. Deploy!
- Click "Create Web Service"
- Wait 5-10 minutes
- Access your app at `https://your-app.onrender.com`

---

## 🔑 Critical Environment Variables

**Required:**
- `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `DATABASE_URL` - Use **Internal Database URL** from PostgreSQL service
- `PORT` - Always set to `$PORT` (Render provides this)

**Important:**
- `DEBUG=false` in production
- `ENVIRONMENT=production`
- `CORS_ORIGINS` - Include your frontend URL

---

## 📝 Start Command Options

**Option 1 (Recommended):**
```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

**Option 2 (Using start script):**
```bash
python working_start.py
```

**Option 3 (Using render_start.py):**
```bash
python render_start.py
```

---

## ✅ Verify Deployment

1. Health Check: `https://your-app.onrender.com/health`
2. API Docs: `https://your-app.onrender.com/docs`
3. Check Logs: Render Dashboard → Your Service → "Logs"

---

## 🆘 Common Issues

**App won't start:**
- Check logs in Render Dashboard
- Verify `PORT=$PORT` in environment variables
- Ensure `requirements.txt` has all dependencies

**Database errors:**
- Use **Internal Database URL** (not external)
- Verify `psycopg2-binary` in requirements.txt
- Check database service is running

**CORS errors:**
- Add frontend URL to `CORS_ORIGINS`
- Format: `https://frontend.onrender.com,https://yourdomain.com`

---

For detailed instructions, see `RENDER_DEPLOYMENT_GUIDE.md`

