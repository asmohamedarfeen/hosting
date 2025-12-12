# ✅ Render Deployment Checklist

Use this checklist to ensure a smooth deployment to Render.

## Pre-Deployment

- [ ] Code is committed and pushed to Git repository
- [ ] All sensitive data removed from code (use environment variables)
- [ ] `.env` file is in `.gitignore` (never commit secrets)
- [ ] `requirements.txt` includes all dependencies
- [ ] Database migrations are tested locally
- [ ] Application runs successfully locally

## Render Setup

- [ ] Created Render account
- [ ] Connected Git repository to Render
- [ ] Created PostgreSQL database service
- [ ] Copied Internal Database URL
- [ ] Created Web Service
- [ ] Configured build and start commands

## Environment Variables

- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=false`
- [ ] `SECRET_KEY` (strong, randomly generated)
- [ ] `DATABASE_URL` (Internal Database URL)
- [ ] `HOST=0.0.0.0`
- [ ] `PORT=$PORT`
- [ ] `CORS_ORIGINS` (if using frontend)
- [ ] `ALLOWED_HOSTS` (your Render domain)
- [ ] `GOOGLE_CLIENT_ID` (if using OAuth)
- [ ] `GOOGLE_CLIENT_SECRET` (if using OAuth)
- [ ] `GOOGLE_REDIRECT_URI` (updated for Render domain)
- [ ] `GEMINI_API_KEY` (if using Gemini AI)

## Post-Deployment

- [ ] Application starts without errors
- [ ] Health endpoint returns 200: `/health`
- [ ] API docs accessible: `/docs`
- [ ] Database connection successful
- [ ] Database tables created (check logs)
- [ ] Static files serving correctly
- [ ] File uploads working (or using external storage)
- [ ] OAuth callbacks working (if applicable)
- [ ] CORS configured correctly
- [ ] Custom domain configured (if applicable)

## Security

- [ ] `DEBUG=false` in production
- [ ] Strong `SECRET_KEY` generated
- [ ] No secrets in code or logs
- [ ] HTTPS enabled (automatic on Render)
- [ ] CORS origins limited to trusted domains
- [ ] Database uses Internal URL (not external)

## Monitoring

- [ ] Logs accessible in Render Dashboard
- [ ] Error tracking set up (if using Sentry)
- [ ] Health checks configured
- [ ] Backup strategy in place

## Performance

- [ ] Workers configured appropriately
- [ ] Static files optimized
- [ ] Database queries optimized
- [ ] Caching configured (if applicable)

---

## Quick Commands Reference

**Generate Secret Key:**
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Test Database Connection (Render Shell):**
```python
python -c "from database_enhanced import test_db_connection; print('OK' if test_db_connection() else 'FAILED')"
```

**Run Migrations (Render Shell):**
```python
python -c "from database_enhanced import init_database; init_database()"
```

**Check App Status:**
```bash
curl https://your-app.onrender.com/health
```

---

**Last Updated**: 2025-01-27

