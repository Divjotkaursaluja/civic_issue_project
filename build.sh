#!/usr/bin/env bash
set -o errexit

python -m pip install --upgrade pip
pip install -r requirements.txt
python civicbackend/manage.py collectstatic --no-input
python civicbackend/manage.py migrate
