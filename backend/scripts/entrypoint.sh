#!/bin/bash
set -e

if [ "$APP_MODE" != "production" ]; then
  # Запуск скрипта инициализации S3
  python /code/scripts/init_s3.py

  # Запуск скрипта инициализации базы
  python /code/scripts/init_db.py

  # Запуск скрипта инициализации данных
  python /code/scripts/init_data.py
fi

# Запуск FastAPI
exec uvicorn main:app --host 0.0.0.0 --port 8000 --forwarded-allow-ips=* --proxy-headers --no-server-header
