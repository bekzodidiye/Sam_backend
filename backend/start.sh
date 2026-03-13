#!/bin/bash

# Exit on error
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating media directories..."
mkdir -p media/checkin_photos media/sales_links media/avatars

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser..."
python manage.py createsuperuser --noinput || echo "Superuser already exists or environment variables not set."

echo "Starting Daphne..."
daphne -b 0.0.0.0 -p $PORT config.asgi:application
