#!/usr/bin/env bash
# exit on error
set -o errexit

# تثبيت تبعيات النظام التي تحتاجها Pillow
apt-get update && apt-get install -y libjpeg-dev zlib1g-dev

# تثبيت مكتبات بايثون
pip install -r requirements.txt
