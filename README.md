# BORS — Bus Operator Returns System

Internal NTA web application for collecting annual returns from licensed bus operators. Built with Django. Deployed on Render (or any WSGI host).

---

## Table of Contents

1. [What the system does](#what-the-system-does)
2. [First-time setup](#first-time-setup)
3. [Annual collection process](#annual-collection-process)
4. [Seeding operator data](#seeding-operator-data)
5. [Locking a collection year](#locking-a-collection-year)
6. [Test mode](#test-mode)
7. [Downloading submissions](#downloading-submissions)
8. [Admin reference](#admin-reference)
9. [Running locally](#running-locally)
10. [Deployment (Render)](#deployment-render)

---

## What the system does

Operators log in with a unique token (emailed by NTA staff) and complete a five-step return:

| Step | Section | What operators fill in |
|------|---------|------------------------|
| 1 | General | Operator name, county, annual revenue, TaxSaver participation |
| 2 | Licences | Per-route: passengers, km, daily PVR, Free Travel, YASC |
| 3 | Emissions | Per-vehicle: make/model, fuel type, Euro standard, AVL/GPS, route usage % |
| 4 | Accessibility | Per-vehicle: wheelchair access, ramps, displays, audio, induction loop |
| 5 | Declaration | Signed declaration before final submission |

NTA staff can pre-populate routes and vehicle details (from existing NTA records) before operators log in. Operators see this data pre-filled but can edit it.

---

## First-time setup

### Prerequisites

- Python 3.10+
- pip

### Install

```bash
git clone <repo-url>
cd bors

python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### Configure environment

Copy the variables below into a `.env` file or set them in your hosting dashboard:

| Variable | Required | Example |
|----------|----------|---------|
| `SECRET_KEY` | Yes | `django-insecure-...` (generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`) |
| `DATABASE_URL` | No (defaults to SQLite) | `postgres://user:pass@host/dbname` |
| `DEBUG` | No (defaults to True) | `False` in production |
| `ALLOWED_HOSTS` | No (defaults to `*`) | `bors.nationaltransport.ie` |

### Initialise the database

```bash
python manage.py migrate
```

### Create a staff account

```bash
python manage.py createsuperuser
```

This account is used to log in to the admin area (`/admin/`) and the NTA staff pages (`/tokens/`).

### Run locally

```bash
python manage.py runserver
```

| URL | Purpose |
|-----|---------|
| `http://127.0.0.1:8000/` | Operator-facing home page |
| `http://127.0.0.1:8000/admin/` | Django admin |
| `http://127.0.0.1:8000/tokens/` | NTA staff: token manager |
| `http://127.0.0.1:8000/staff/seed-import/` | NTA staff: seed data upload |
| `http://127.0.0.1:8000/staff/locks/` | NTA staff: year lock manager |

---

## Annual collection process

Follow these steps at the start of each new data collection year (e.g. collecting 2026 data in early 2027).

### Step 1 — Add / update operators

Go to `/tokens/` and use the **Add New Operator** form (Operator Name + Email) to create accounts one at a time. A token is generated automatically.

Alternatively, add operators in bulk via the **Operators sheet** in a seed import file at `/staff/seed-import/` (see [Seeding operator data](#seeding-operator-data)).

Then click **Regenerate All Tokens** at `/tokens/` to invalidate any tokens from the previous year and issue fresh ones. Do this _before_ sending any emails.

### Step 2 — Prepare seed data (optional but recommended)

Pre-seeding routes and vehicles saves operators time and reduces errors. See [Seeding operator data](#seeding-operator-data) for full details.

### Step 3 — Send access codes to operators

Go to `/tokens/` and click the **envelope icon** next to each operator. This copies a ready-made email to your clipboard — paste it into Outlook (or your email client) and send.

The email contains:
- The operator's unique access code
- A link to the BORS login page (`/access/`)

### Step 4 — Monitor submissions

The Token Manager shows each operator's return status: **Draft** (started, not submitted) or **Submitted**.

Check back periodically and chase operators who have not submitted by the deadline.

### Step 5 — Lock the year and download submissions

Once the collection period closes:

1. Go to `/staff/locks/` and lock the collection year. This immediately prevents all operators from editing or submitting returns for that year. They can still view and download their submitted return.
2. Go to `/tokens/` and use the download buttons in the top-right corner:

| Button | File | Contents |
|--------|------|----------|
| Download All (Excel) | `BORS_All_Operators.xlsx` | 6 sheets: General, Licences, Emissions, Vehicle Route Usage, Accessibility, Declarations |
| Download All (JSON) | `BORS_All_Operators.json` | Full nested data for all operators |

Both files include all operators regardless of submission status (draft returns are included).

---

## Seeding operator data

Seed data pre-populates routes and vehicles for operators before they start their return. It is tied to a specific **data year** so each year's seed data is kept separate.

### What gets pre-filled

| Panel | Pre-filled from seed | Operator fills in |
|-------|---------------------|-------------------|
| Step 2 Licences | Route No | All Y/N columns, passenger numbers, km, PVR |
| Step 3 Emissions | RES ID, Reg No, Make, Model, Transmission, Engine Type, Seats on Record | Y/N fields, fuel type, Euro standard, route usage % |

Seed data is applied the **first time** an operator visits Step 2 or Step 3. It will never overwrite data an operator has already entered.

### Uploading via the web UI

1. Go to `/staff/seed-import/` → **Download Template**
2. Fill in the sheets:

   **Operators sheet** — creates operator accounts (skips existing)

   | Operator Name | Email |
   |---|---|
   | Callinan Coaches Ltd | info@callinan.ie |

   **Licences sheet**

   | Operator Name | Route No |
   |---|---|
   | Callinan Coaches Ltd | 763 |
   | Callinan Coaches Ltd | 251_251X |

   **Vehicles sheet**

   | Operator Name | RES ID | Vehicle Reg No | Make | Model Version | Transmission | Engine Type | Seats on Record |
   |---|---|---|---|---|---|---|---|
   | Callinan Coaches Ltd | 1 | 07G17925 | SCANIA | OTHER | OTHER | DIESEL | 68 |

   - **Operator Name** must match exactly what is shown in the Token Manager.
   - **RES ID** is the sequential row number (1, 2, 3 …).
   - Leave any unknown fields blank — operators can fill them in.

3. Set the **Data Year** field on the upload form to the collection year.
4. Upload the completed file.

The current seed data table below the form can be filtered by year to review what has been loaded.

### Uploading via command line

```bash
# Import all .xlsx files from the seed_data/ folder for a given year
python manage.py ingest_seed --year 2025

# Import a specific file
python manage.py ingest_seed --year 2025 --file path/to/file.xlsx
```

### Clearing seed data

Seed data is stored in the database. To remove it, use the Django admin at `/admin/` → **Seed Licences** or **Seed Vehicles** and filter by year.

Removing seed data does not affect returns that have already been started — operator-entered data is separate.

---

## Locking a collection year

Once the collection period for a year is closed, lock that year to prevent operators from making any further changes.

### Lock a year

Go to `/staff/locks/`, enter the year, and click **Lock Year**.

- Operators immediately lose the ability to save or submit returns for that year.
- They can still view their submitted return and download their Excel export.
- All form fields are shown as read-only in their browser.

### Unlock a year

On the same page, click **Unlock** next to the locked year. Operators can edit and submit again immediately.

The lock manager is also accessible from the **Year Locks** button on the Token Manager page.

---

## Test mode

Use test mode to run through the full operator workflow without creating real submission data.

### Mark an operator as a test account

Go to `/tokens/` and click the **flask icon** in the operator's row. The icon turns amber and a **TEST** badge appears on the operator's row and on their return page.

### Clear test submissions

```bash
# Dry-run — shows how many records would be deleted
python manage.py clear_submissions --test-only

# Actually delete
python manage.py clear_submissions --test-only --confirm
```

This deletes all returns (and their licences, emissions, accessibility records, and declarations) belonging to test operators only. Real operator data is untouched.

### Clear all submissions

```bash
# Dry-run
python manage.py clear_submissions --all

# Actually delete
python manage.py clear_submissions --all --confirm
```

Operator access tokens and seed data are never deleted by either command.

---

## Downloading submissions

### Excel export (bulk — all operators)

`/tokens/` → **Download All (Excel)**

Sheets in the workbook:

| Sheet | Contents |
|-------|----------|
| General | One row per operator return |
| Licences | All route data across all operators |
| Emissions | All vehicle emission data |
| Vehicle Route Usage | Per-vehicle route usage percentages |
| Accessibility | All vehicle accessibility data |
| Declarations | Signed declarations |

### JSON export (bulk — all operators)

`/tokens/` → **Download All (JSON)**

Returns a list of operator objects, each with fully nested licences, emissions (including route usage), accessibility, and declaration.

### Excel export (single operator)

Available from the operator's own success page after they submit. Operators can download their own data only.

---

## Admin reference

### Key URLs

| URL | Who uses it | Purpose |
|-----|------------|---------|
| `/admin/` | NTA staff | Django admin — view/edit all data directly |
| `/tokens/` | NTA staff | Create operators, manage tokens, download data |
| `/staff/seed-import/` | NTA staff | Upload pre-populated routes and vehicles |
| `/staff/seed-template/` | NTA staff | Download blank seed Excel template |
| `/staff/locks/` | NTA staff | Lock / unlock a collection year |
| `/staff/export/excel/` | NTA staff | Bulk Excel download |
| `/staff/export/json/` | NTA staff | Bulk JSON download |
| `/access/` | Operators | Token login page |

### Management commands

```bash
# Import seed data for a specific year from the seed_data/ folder
python manage.py ingest_seed --year 2025

# Import from a specific file
python manage.py ingest_seed --year 2025 --file seed_data/2025_seed.xlsx

# Clear test submissions (dry-run — no changes made)
python manage.py clear_submissions --test-only

# Clear test submissions (destructive)
python manage.py clear_submissions --test-only --confirm

# Clear ALL submissions (destructive)
python manage.py clear_submissions --all --confirm

# Apply all database migrations (run after code updates)
python manage.py migrate

# Create a new staff account
python manage.py createsuperuser
```

### Data year

The data year is set by the operator in Step 1 (General) and by staff when uploading seed data. Each return carries its own year, so the same operator can have returns for different years in the database simultaneously. Year locks are applied per year and affect all operators.

---

## Running locally

```bash
# Activate virtual environment
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac / Linux

# Apply any new migrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

The app runs at `http://127.0.0.1:8000/`.

To log in as staff, go to `http://127.0.0.1:8000/admin/` with the superuser credentials created during setup.

---

## Deployment (Render)

The project is configured for Render via `render.yaml` and `build.sh`.

### Environment variables to set in Render dashboard

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | A long random string (generate one locally — see First-time setup) |
| `DATABASE_URL` | Provided automatically by Render PostgreSQL |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | Your Render domain, e.g. `bors.onrender.com` |

### Deploying a code update

1. Push the changes to the connected git branch.
2. Render builds and deploys automatically.
3. If the update includes new migrations (new `0xxx_*.py` files in `returns/migrations/`), they run automatically during the build via `build.sh`.

### After deploying for the first time

1. Open the Render shell (or connect via SSH) and run:
   ```bash
   python manage.py createsuperuser
   ```
2. Log in at `https://<your-domain>/admin/` to confirm it works.
3. Go to `/tokens/` to start adding operators.
