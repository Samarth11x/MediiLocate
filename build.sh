#!/usr/bin/env bash
# ==============================================================================
# MediLocate AI — Production Build Script for Render
# Compiles Vite React frontend with PWA service worker and manifest,
# installs backend dependencies, collects static files with WhiteNoise,
# and executes database migrations on PostgreSQL.
# ==============================================================================

set -o errexit

echo "===================================================================="
echo "--> 1. Building Vite React Frontend & PWA Assets"
echo "===================================================================="
cd frontend
npm ci || npm install
npm run build
cd ..

echo "===================================================================="
echo "--> 2. Installing Backend Python Dependencies"
echo "===================================================================="
cd backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "===================================================================="
echo "--> 3. Collecting Static Files with WhiteNoise"
echo "===================================================================="
python manage.py collectstatic --no-input

echo "===================================================================="
echo "--> 4. Executing Database Migrations"
echo "===================================================================="
python manage.py migrate --no-input
cd ..

echo "===================================================================="
echo "--> 5. Build Completed Successfully for Production Deployment"
echo "===================================================================="
