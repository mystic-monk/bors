#!/usr/bin/env bash
set -e
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser from environment variables if it doesn't exist yet.
# Set DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD
# in the Render dashboard → Environment tab before deploying.
if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
  python manage.py createsuperuser \
    --no-input \
    --username "$DJANGO_SUPERUSER_USERNAME" \
    --email "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" \
    2>/dev/null || echo "Superuser already exists — skipping."
fi
