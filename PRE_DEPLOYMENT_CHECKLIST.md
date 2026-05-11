# Pre-Deployment Checklist - TourVista on Render

Complete this checklist before deploying your app to Render.

---

## 📋 Code Preparation

- [ ] All code committed and pushed to GitHub
- [ ] No sensitive data (passwords, API keys) in code
- [ ] All required dependencies in `requirements.txt`
- [ ] Project runs locally without errors (`python manage.py runserver`)
- [ ] No print statements or debug code left in production code

---

## 🔧 Configuration Files

- [ ] `Procfile` exists and contains release & web commands
- [ ] `runtime.txt` specifies Python 3.11.8
- [ ] `requirements.txt` includes:
  - [ ] `psycopg2-binary` (PostgreSQL driver)
  - [ ] `gunicorn` (production WSGI server)
  - [ ] `whitenoise` (static files serving)
  - [ ] `dj-database-url` (database URL parsing)
- [ ] `settings.py` updated with:
  - [ ] WhiteNoise middleware added
  - [ ] Database configuration supports PostgreSQL
  - [ ] Static files configured properly
  - [ ] Security settings for production
  - [ ] CSRF_TRUSTED_ORIGINS configured

---

## 🔐 Environment Setup

- [ ] `SECRET_KEY` generated (strong random string)
- [ ] `DEBUG=False` for production
- [ ] `ALLOWED_HOSTS` includes your domain and Render URL
- [ ] `CSRF_TRUSTED_ORIGINS` configured for your domain
- [ ] Database credentials ready
- [ ] Email credentials (Gmail App Password if using Gmail)

---

## 🗄️ Database Preparation

- [ ] PostgreSQL database created on Render
- [ ] DATABASE_URL copied correctly
- [ ] Database credentials stored securely
- [ ] Migrations tested locally

---

## 📁 Static & Media Files

- [ ] `python manage.py collectstatic` runs without errors locally
- [ ] Static files directory configured
- [ ] Media files consideration:
  - [ ] Using local storage (files lost on redeploy) OR
  - [ ] Configured AWS S3 or similar service for persistent storage

---

## 🌐 Domain & SSL

- [ ] Custom domain registered (or ready to use Render's subdomain)
- [ ] DNS provider account ready (if using custom domain)
- [ ] Ready to add CNAME records
- [ ] SSL certificate auto-provisioned by Render (automatic)

---

## ✅ Final Checks

- [ ] README.md updated with deployment instructions
- [ ] `.gitignore` includes `.env` (never commit secrets)
- [ ] Local database backup taken (if needed)
- [ ] All tests passing locally
- [ ] GitHub repository public or Render has access

---

## 📱 Render Setup Checklist

- [ ] Render account created at [https://render.com](https://render.com)
- [ ] GitHub connected to Render account
- [ ] Ready to configure:
  - [ ] Web Service name
  - [ ] Build & start commands
  - [ ] Environment variables
  - [ ] PostgreSQL database
  - [ ] Custom domain (if applicable)

---

## 🚀 Ready to Deploy?

Once all checkboxes are complete, follow [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) to deploy your app!

---

## 📚 Quick Reference

**Generate Django SECRET_KEY:**
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

**Test static files locally:**
```bash
python manage.py collectstatic --no-input
```

**Run development server:**
```bash
python manage.py runserver
```

**Check for missing dependencies:**
```bash
pip check
```

---

**Need Help?**
- See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions
- Check Render docs: [https://render.com/docs](https://render.com/docs)
- Django docs: [https://docs.djangoproject.com/](https://docs.djangoproject.com/)
