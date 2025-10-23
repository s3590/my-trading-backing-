#!/usr/bin/env bash
# exit on error
set -o errexit

echo "--- Starting build script ---"

# تثبيت تبعيات النظام
apt-get update && apt-get install -y libjpeg-dev zlib1g-dev

echo "--- System dependencies installed ---"

# تثبيت مكتبات بايثون
pip install -r requirements.txt

echo "--- Python packages installed successfully ---"
