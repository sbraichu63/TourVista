# TourVista Deployment Guide - Render

This guide walks you through deploying your TourVista Django application to [Render](https://render.com) with PostgreSQL database and a custom domain.

---

## 📋 Prerequisites

Before deploying, ensure you have:

1. **GitHub Repository** - Push your code to GitHub (required by Render)
2. **Render Account** - Sign up at [https://render.com](https://render.com)
3. **PostgreSQL Database URL** - Provided by Render
4. **Custom Domain** (optional) - DNS already configured (optional for testing)

---

## 🔧 Step 1: Prepare Your Project for Deployment

All necessary files have been created:
- ✅ `Procfile` - Tells Render how to run your app
- ✅ `runtime.txt` - Specifies Python version (3.11.8)
- ✅ `requirements.txt` - Updated with production packages
- ✅ `settings.py` - Updated with production settings

### Required Environment Variables
Your app needs these environment variables on Render:

```
DEBUG=False
SECRET_KEY=<generate-a-strong-random-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,tourvistaapp.render.com
DATABASE_URL=<provided-by-Render>
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://tourvistaapp.render.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=<app-specific-password>
```

---

## 🚀 Step 2: Deploy on Render

### Option A: Using Render Dashboard (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Create New Web Service on Render**
   - Go to [https://dashboard.render.com](https://dashboard.render.com)
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository
   - Select the TourVista repository and branch

3. **Configure Web Service**
   - **Name**: `tourvista` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --no-input`
   - **Start Command**: `gunicorn tourvista.wsgi` (should auto-detect from Procfile)
   - **Instance Type**: Choose appropriate plan (Starter for testing)

4. **Add Environment Variables**
   - Click **"Environment"** tab
   - Add all environment variables listed above
   - **IMPORTANT**: Generate a strong SECRET_KEY (use an online generator)

5. **Create PostgreSQL Database**
   - On Render Dashboard, click **"New +"** → **"PostgreSQL"**
   - **Name**: `tourvista-db`
   - **Database**: `tourvista`
   - **User**: `tourvista`
   - **Region**: Choose same region as web service
   - Copy the **Internal Database URL**

6. **Add Database URL to Web Service**
   - Go back to your Web Service
   - Add environment variable: `DATABASE_URL=<internal-database-url>`

7. **Deploy**
   - Click **"Create Web Service"**
   - Render will automatically build and deploy your app
   - Monitor the deployment logs

---

## 🗄️ Step 3: Setup Database

After successful deployment:

1. **Run Migrations**
   - Render automatically runs migrations via the `Procfile` release phase
   - Check deployment logs to confirm migrations completed

2. **Create Superuser** (optional, for admin access)
   ```bash
   # Connect via Render Shell
   # In your service's "Shell" tab, run:
   python manage.py createsuperuser
   ```

---

## 🌐 Step 4: Configure Custom Domain (Optional)

1. **On Render Dashboard**
   - Go to your Web Service
   - Click **"Settings"** tab
   - Under **"Custom Domains"**, click **"Add Custom Domain"**
   - Enter your domain (e.g., `tourvista.com`)

2. **Update DNS Settings**
   - Follow Render's instructions for your DNS provider
   - Add the CNAME record provided by Render
   - Wait for DNS propagation (5-30 minutes)

3. **Update Environment Variables**
   - Add your domain to `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`
   - Example:
     ```
     ALLOWED_HOSTS=tourvista.com,www.tourvista.com
     CSRF_TRUSTED_ORIGINS=https://tourvista.com,https://www.tourvista.com
     ```

---

## 🔐 Step 5: Security Setup

### Generate SECRET_KEY

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Then add the generated key to your Render environment variables.

### Email Configuration (Gmail)

1. Enable 2-Step Verification on your Gmail account
2. Create an App Password:
   - Go to [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - Select "Mail" and "Windows Computer"
   - Copy the generated 16-character password
3. Set as `EMAIL_HOST_PASSWORD` on Render

### SSL/HTTPS

- Render automatically provisions SSL certificates
- All traffic is HTTPS by default

---

## 📊 Step 6: Verify Deployment

1. **Check Your Domain**
   - Visit `https://yourdomain.render.com` (or your custom domain)
   - Verify the app loads correctly

2. **View Logs**
   - In Render Dashboard, check the "Logs" tab
   - Look for any errors or warnings

3. **Test Admin Panel**
   - Visit `https://yourdomain.render.com/admin`
   - Login with your superuser credentials

---

## 🐛 Troubleshooting

### Common Issues

**Build Failed**
- Check build logs for errors
- Ensure all dependencies are in `requirements.txt`
- Verify Python syntax in your code

**500 Error**
- Check logs: `Logs` tab in Render Dashboard
- Verify `SECRET_KEY` is set
- Ensure `DATABASE_URL` is correct

**Static Files Not Loading**
- Ensure `python manage.py collectstatic` runs successfully
- Check `STATIC_ROOT` and `STATIC_URL` settings

**Database Connection Error**
- Verify `DATABASE_URL` is correct
- Ensure PostgreSQL service is running
- Check connection string format: `postgresql://user:password@host:port/database`

**Email Not Sending**
- Verify `EMAIL_HOST_PASSWORD` is an App Password (not your Gmail password)
- Check email settings in Render environment variables

---

## 🔄 Deployment Updates

After making code changes:

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

2. **Automatic Redeployment**
   - Render automatically rebuilds and deploys on every push to your main branch
   - Monitor the deployment in the "Logs" tab

---

## 📱 Media Files & User Uploads

By default, Render uses ephemeral storage. For persistent file uploads:

1. **Option A: Use AWS S3** (Recommended)
   - Configure boto3 and django-storages
   - Store `MEDIA_ROOT` and `STATIC_ROOT` on S3

2. **Option B: Local Storage**
   - Files persist only during deployment
   - User uploads will be lost on redeployment

For production, **S3 or similar cloud storage is recommended**.

---

## 📞 Support

For Render-specific issues, visit:
- [Render Docs](https://render.com/docs)
- [Render Support](https://support.render.com)

For Django issues:
- [Django Documentation](https://docs.djangoproject.com/)

---

**Good luck with your deployment! 🎉**
