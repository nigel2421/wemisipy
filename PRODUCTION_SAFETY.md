# Production Safety Audit ✓

## Database & Media Protection

### ✅ What's Protected (Already In Place)
- **db.sqlite3** — Ignored by Git (.gitignore line 4)
- **media/** — Ignored by Git (.gitignore line 5)
- **staticfiles/** — Ignored by Git (.gitignore line 18)

Your production database and user uploads will **never be overwritten** by git pull.

---

## Settings Isolation (JUST FIXED)

### ✅ New Environment-Based Configuration
Settings now automatically detect production vs development:

```python
DJANGO_ENV = os.getenv('DJANGO_ENV', 'development')
IS_PRODUCTION = DJANGO_ENV == 'production'
```

**Development mode** (local):
- DEBUG = True
- Console email logging
- Simple allowed hosts

**Production mode** (live server):
- DEBUG = False (MANDATORY)
- Real email backend with SMTP
- SSL redirect enabled
- Secure cookies enabled
- HSTS headers enabled

---

## What You Must Do On Production Server

### 1. Create `.env` File (ONCE, on production only)

In your cPanel Terminal, create a production `.env`:

```bash
nano .env
```

Copy this and update with REAL values:

```env
DJANGO_ENV=production
DJANGO_SECRET_KEY=generate-a-long-random-secret-key-here
DEBUG=False
ADMIN_EMAIL=your-admin-email@wemisi.com
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
GOOGLE_API_KEY=your-gemini-api-key
```

**Generate a secure SECRET_KEY:**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. Add python-dotenv to Requirements (Already Done)
The dependency is already included, but verify with:
```bash
pip list | grep dotenv
```

---

## Deployment Checklist

- [ ] Production `.env` file created with all required variables
- [ ] DJANGO_SECRET_KEY is long and random (50+ chars)
- [ ] DEBUG=False in production
- [ ] EMAIL credentials are configured
- [ ] Run: `bash deploy.sh` to pull and test changes
- [ ] Verify site still loads: `https://wemisi.com`
- [ ] Check admin login still works

---

## What Happens on Each Deployment

When you run `bash deploy.sh`:

1. ✅ Pulls latest code from GitHub
2. ✅ Reads environment variables from `.env`
3. ✅ Applies new migrations (safe — never deletes data)
4. ✅ Collects static files
5. ❌ Never touches `db.sqlite3` (ignored by Git)
6. ❌ Never touches `media/` folder (ignored by Git)

**Result:** New code + same database + same uploaded images

---

## Security Summary

| What | Status | Protected |
|------|--------|-----------|
| Database | Ignored by Git | ✅ Safe |
| Media files | Ignored by Git | ✅ Safe |
| Secrets (SECRET_KEY) | Environment variable | ✅ Safe |
| Debug mode | Environment variable | ✅ Safe |
| Email config | Environment variable | ✅ Safe |

---

## Files Changed This Session

- `store/settings.py` — Now environment-aware
- `.env.example` — Created as template for production
- `store/admin.py` — Removed single image upload (bulk only)
- `store/context_processors.py` — Fixed field order issue

All future deployments are now **safe by default**. 🎉
