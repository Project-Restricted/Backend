#!/usr/bin/env bash
# Устанавливаем зависимости
pip install --upgrade pip
pip install -r requirements.txt

# Миграции
python manage.py migrate

# Статика
python manage.py collectstatic --noinput
