#!/bin/bash
source venv/bin/activate

# # https://stackoverflow.com/a/43929298/8608146
# watchmedo auto-restart -p '(tasks|tasks/__init__)*.py' \
# watchmedo auto-restart -p '*.py' \
# --ignore-directories \
# --ignore-patterns './venv/*' \
# --recursive \
# -- python server/scripts/celery.py

echo "[INFO] Celery running in PRODUCTION mode"
python server/scripts/celery_split.py
