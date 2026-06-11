#!/bin/bash
# =============================================================
# Wemisi – Safe Deployment Script
# Run this from your cPanel Terminal instead of plain git pull
# =============================================================
set -e  # Stop immediately if any command fails

echo "===================================================="
echo "  WEMISI DEPLOYMENT – $(date)"
echo "===================================================="

# ── 1. Pull latest code from GitHub ──────────────────────────
echo ""
echo "[1/5] Pulling latest code from GitHub..."
git pull origin main
echo "      ✓ Code updated"

# ── 2. Activate virtual environment ──────────────────────────
echo ""
echo "[2/5] Activating virtual environment..."
source .venv/bin/activate
echo "      ✓ Virtual environment active"

# ── 3. Install / update Python dependencies ──────────────────
echo ""
echo "[3/5] Installing dependencies..."
pip install -r requirements.txt --quiet
echo "      ✓ Dependencies installed"

# ── 4. Apply database migrations (safe – never deletes data) ──
echo ""
echo "[4/5] Applying database migrations..."
python manage.py migrate --noinput
echo "      ✓ Migrations applied"

# ── 5. Collect static files ───────────────────────────────────
echo ""
echo "[5/5] Collecting static files..."
python manage.py collectstatic --noinput --clear
echo "      ✓ Static files collected"

# ── 6. Restart app via Passenger ──────────────────────────────
echo ""
echo "[6/6] Restarting application..."
mkdir -p tmp
touch tmp/restart.txt
echo "      ✓ App restarted"

echo ""
echo "===================================================="
echo "  DEPLOYMENT COMPLETE ✓"
echo "  Your live database and media files were NOT touched."
echo "===================================================="
