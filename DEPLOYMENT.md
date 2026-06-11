# Wemisi – Deployment Guide

## IMPORTANT: One-time Production Setup (do this ONCE from your production server)

### Step 1: Create `.env` File

In your cPanel Terminal, create the environment file:

```bash
nano .env
```

Paste this template and update with YOUR production values:

```env
DJANGO_ENV=production
DJANGO_SECRET_KEY=GENERATE_A_LONG_RANDOM_SECRET_KEY_HERE
DEBUG=False
ADMIN_EMAIL=your-admin-email@wemisi.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
GOOGLE_API_KEY=your-gemini-api-key-if-using-ai
```

**To generate a secure SECRET_KEY**, run:
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Press `Ctrl+X`, then `Y`, then `Enter` to save.

### Step 2: Untrack Database & Media from Git (ONE TIME ONLY)

These commands prevent your live database from being overwritten:

```bash
cd /path/to/wemisipy
git rm --cached db.sqlite3
git rm -r --cached media/
git add .gitignore
git commit -m "chore: protect live db and media from git tracking"
git push origin main
```

After this, `db.sqlite3` and `media/` will never again be included in commits.

---

## How to Deploy from Now On

Instead of running `git pull` manually in cPanel Terminal, use the deploy script:

```bash
# In your cPanel Terminal, from the project root directory:
bash deploy.sh
```

The script will:
1. Pull the latest code from GitHub
2. Activate the virtual environment
3. Install any new Python packages
4. Apply database migrations (safe — never deletes existing data)
5. Collect static files
6. Restart the application

Your **live database** (`db.sqlite3`), **uploaded images** (`media/`), and **environment secrets** (`.env`) are never touched by Git.

---

## Troubleshooting

### Script says "permission denied"
```bash
chmod +x deploy.sh
bash deploy.sh
```

### Virtual environment not found
Edit `deploy.sh` and update the path on line that says `source .venv/bin/activate`
to match your actual venv location (e.g. `source ~/virtualenv/wemisi/3.x/bin/activate`).

### Migrations fail
```bash
python manage.py showmigrations   # see what needs running
python manage.py migrate          # apply manually
```
