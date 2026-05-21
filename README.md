# BORS — Bus Operator Returns System

Internal NTA Django web application for collecting annual returns from licensed bus operators.

## Structure

Four-step wizard matching the existing Excel template:

| Step | Section              | Data collected                                                  |
|------|----------------------|-----------------------------------------------------------------|
| 1    | General Questions    | Operator identity, county, annual revenue, TaxSaver             |
| 2    | Licence Details      | Per-route: passengers, km, PVR, Free Travel, YASC, dates        |
| 3    | Emissions            | Per-vehicle: make/model, fuel type, Euro standard, AVL/GPS      |
| 4    | Accessibility        | Per-vehicle: wheelchair access, displays, ramps, loop system    |

## Setup

```bash
cd bors
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Application runs at: http://127.0.0.1:8000/
Admin panel:         http://127.0.0.1:8000/admin/

## Features

- Multi-step wizard with progress stepper
- Dynamic add/remove rows for licences, vehicles (emissions and accessibility)
- Per-field validation with inline error messages
- Draft and submitted status tracking
- Excel export (matches original BORS template sheet structure)
- Django admin for NTA staff to view and manage all submissions

## Production notes

Before deploying to a server:

1. Set `DEBUG = False` in settings.py
2. Replace `SECRET_KEY` with a value from an environment variable
3. Set `ALLOWED_HOSTS` to your server hostname
4. Switch the database from SQLite to PostgreSQL
5. Run `python manage.py collectstatic`
6. Serve static files via nginx or whitenoise
7. Enable Django's built-in authentication for staff login
