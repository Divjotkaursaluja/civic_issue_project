#!/usr/bin/env bash
set -o errexit

python -m pip install --upgrade pip
pip install -r requirements.txt
python civicbackend/manage.py collectstatic --no-input

if [ "$RUN_MIGRATIONS" = "true" ]; then
  python civicbackend/manage.py migrate
else
  echo "Skipping migrations during build. Set RUN_MIGRATIONS=true to run them."
fi
