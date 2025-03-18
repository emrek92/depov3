#!/bin/bash

# Statik dosyaları topla
pip install -r requirements.txt
python manage.py collectstatic --noinput

# Vercel'in build_files.sh'i build olarak işaretlemesi için bir çıktı klasörü oluşturmamız gerekiyor
if [ -d staticfiles_build ]; then
  rm -rf staticfiles_build
fi

# staticfiles_build klasörü oluştur ve tüm staticfiles içeriğini kopyala
mkdir -p staticfiles_build
cp -r staticfiles/* staticfiles_build/ 