#!/bin/bash

# Python paketlerini yükle
pip install -r requirements.txt

# Statik dosyaları topla
python manage.py collectstatic --noinput

# Veritabanı migrasyonlarını uygula
python manage.py migrate --noinput

# Vercel için gerekli dosyaları oluştur
mkdir -p staticfiles
cp -r static/* staticfiles/ 