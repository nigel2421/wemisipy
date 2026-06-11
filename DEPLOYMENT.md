# Wemisi – Deployment Guide

## One-time Setup (do this ONCE from your local machine)

These commands remove the database and media folder from Git tracking.
**Your live files will not be deleted** — they just stop being tracked by Git.

```bash
# Un-track the database from git history
git rm --cached db.sqlite3

# Un-track the entire media folder from git history
git rm -r --cached media/

# Commit the cleanup
git add .gitignore
git commit -m "chore: protect live db and media from git tracking"
git push origin main
```

After this, `db.sqlite3` and `media/` will never again be included in commits.

---

## How to Deploy from Now On

Instead of running `git pull` manually in cPanel Terminal, run the deploy script:

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

Your **live database** (`db.sqlite3`) and **uploaded images** (`media/`) are never touched.

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
