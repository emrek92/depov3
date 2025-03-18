#!/usr/bin/env bash
# exit on error
set -o errexit

# Pip'i güncelleyelim
python -m pip install --upgrade pip

# Gereksinimleri yükleyelim
pip install -r requirements.txt

# Statik dosyaları toplatalım
python manage.py collectstatic --no-input

# Veritabanı migrasyonlarını uygulayalım
python manage.py migrate 