# Render Deployment Configuration Guide

## Environment Variables for Render

When deploying on Render, you need to set these environment variables in your Web Service dashboard.

### Required Variables

Copy and paste these into Render's environment variables section. Replace the example values with your actual values.

#### Django Core Settings
```
DEBUG=False
SECRET_KEY=<generate-a-strong-random-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,tourvistaapp.render.com
```

#### Database (PostgreSQL)
```
DATABASE_URL=postgresql://tourvista:<password>@<hostname>:5432/tourvista
```
*This is provided by Render when you create the PostgreSQL service*

#### CSRF Security
```
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://tourvistaapp.render.com
```

#### Email Configuration (Gmail)
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=<app-specific-password>
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=TourVista <noreply@yourdomain.com>
```

### Optional Variables

```
OPENWEATHERMAP_API_KEY=<your-api-key>
GEMINI_API_KEY=<your-api-key>
```

---

## Generating SECRET_KEY

The `SECRET_KEY` is critical for security. Generate a strong random key:

### Option 1: Using Django (Recommended)
```bash
python manage.py shell
>>> from django.core.management.utils import get_random_secret_key
>>> print(get_random_secret_key())
```

### Option 2: Using Python
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Option 3: Using Online Generator
- Visit: https://djecrety.ir/
- Copy the generated key

---

## Gmail App Password Setup

Gmail requires an **App Password** for third-party applications (regular Gmail password won't work).

1. **Enable 2-Step Verification** on your Gmail account
   - Go to [https://myaccount.google.com/security](https://myaccount.google.com/security)
   - Enable 2-Step Verification if not already done

2. **Generate App Password**
   - Go to [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - Select "Mail" and "Windows Computer" (or appropriate device)
   - Click "Generate"
   - Copy the 16-character password (without spaces)

3. **Use in Render**
   - Set `EMAIL_HOST_PASSWORD=<16-character-password>`
   - Do NOT use your regular Gmail password

---

## Render Service Links

1. **Create Web Service**: https://dashboard.render.com/new/web
2. **Create PostgreSQL Database**: https://dashboard.render.com/new/database
3. **Dashboard**: https://dashboard.render.com

---

## Environment Variables Format

When entering in Render dashboard:
- Each variable on a new line
- Format: `KEY=VALUE` (no spaces around =)
- Multi-line values: Not supported (keep as single line)

### Example:
```
DEBUG=False
SECRET_KEY=django-insecure-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
ALLOWED_HOSTS=tourvista.com,www.tourvista.com,tourvista.render.com
DATABASE_URL=postgresql://user:pass@host:5432/tourvista
```

---

## Database URL Format

PostgreSQL connection string format:
```
postgresql://username:password@hostname:port/database
```

Example:
```
postgresql://tourvista:MyPassword123@dpg-1234567.render.com:5432/tourvista
```

---

## Domain Configuration

### Using Render's Default Domain
Your app will be available at:
```
https://your-service-name.render.com
```

Update `ALLOWED_HOSTS`:
```
ALLOWED_HOSTS=your-service-name.render.com
```

### Using Custom Domain
Add your custom domain to `ALLOWED_HOSTS`:
```
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-service-name.render.com
```

Then configure DNS (CNAME record) as instructed by Render.

---

## Build & Start Commands

These are set automatically from your `Procfile`, but if you need to set them manually:

**Build Command:**
```
pip install -r requirements.txt && python manage.py collectstatic --no-input
```

**Start Command:**
```
gunicorn tourvista.wsgi
```

---

## Common Configuration Issues

### "ModuleNotFoundError: No module named 'psycopg2'"
- ✅ Ensure `psycopg2-binary` is in `requirements.txt`
- ✅ Rebuild your service on Render

### "SECRET_KEY is required"
- ✅ Set `SECRET_KEY` environment variable on Render
- ✅ Ensure `DEBUG=False`

### "ALLOWED_HOSTS error"
- ✅ Add your domain to `ALLOWED_HOSTS` variable
- ✅ Include both domain and Render subdomain

### "Static files not loading"
- ✅ Ensure build command runs `collectstatic`
- ✅ Check that WhiteNoise middleware is enabled in settings.py
- ✅ Verify `STATIC_ROOT` and `STATIC_URL` are set

### "Email not sending"
- ✅ Use Gmail App Password, not regular Gmail password
- ✅ Check `EMAIL_HOST_USER` is correct email
- ✅ Verify `EMAIL_PORT=587`

---

## Verifying Configuration

After deployment, verify your setup:

1. **Check logs**
   - Visit Render dashboard → Your Service → Logs
   - Look for any warnings or errors

2. **Test your site**
   - Visit your domain
   - Check that static files load (CSS, images, JS)

3. **Test admin panel**
   - Visit `/admin`
   - Verify you can login

4. **Check migrations**
   - Logs should show successful migrations
   - Try accessing database-dependent features

---

## Support

- **Render Documentation**: https://render.com/docs
- **Django Documentation**: https://docs.djangoproject.com/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/

---

**Last updated**: May 2026
