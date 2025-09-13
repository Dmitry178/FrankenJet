#!/bin/bash
set -e

# Запуск скрипта инициализации
python /code/scripts/init_db.py

# Запуск FastAPI
exec uvicorn main:app --host 0.0.0.0 --port 8000 --forwarded-allow-ips=* --proxy-headers --no-server-header
