# BORS — Bus Operator Returns System

Internal NTA web application for collecting annual returns from licensed bus operators. Built with Django. Deployed on Render (or any WSGI host).

---

## Table of Contents

1. [What the system does](#what-the-system-does)
2. [First-time setup](#first-time-setup)
3. [Annual collection process](#annual-collection-process)
4. [Seeding operator data](#seeding-operator-data)
5. [Downloading submissions](#downloading-submissions)
6. [Admin reference](#admin-reference)
7. [Running locally](#running-locally)
8. [Deployment (Render)](#deployment-render)

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

---

## Annual collection process

Follow these steps at the start of each new data collection year (e.g. collecting 2026 data in early 2027).

### Step 1 — Add / update operators

Go to `/staff/seed-import/` → **Download Template**. Fill in the **Operators sheet** (Operator Name, Email) with every operator for this year's collection, then upload the file.

- New operators are created automatically with a token generated.
- Operators already in the system are skipped — no duplicates.
- You can also add individual operators manually at `/tokens/` if needed.

Then go to `/tokens/` and click **Regenerate All Tokens** to invalidate any previous tokens and issue fresh ones for every operator. Do this _before_ sending any emails.

### Step 2 — Prepare seed data (optional but recommended)

NTA has existing records for routes and vehicles. Pre-seeding this data saves operators time and reduces errors.

1. Go to `/staff/seed-import/` → **Download Template**
2. Fill in the two sheets:

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

3. Upload the completed file at `/staff/seed-import/`.

   Alternatively, place the file in the `seed_data/` folder and run:

   ```bash
   python manage.py ingest_seed
   # or for a specific file:
   python manage.py ingest_seed --file path/to/file.xlsx
   ```

Seed data is applied the **first time** an operator visits Step 2 or Step 3. It will never overwrite data an operator has already entered.

### Step 3 — Send access codes to operators

Go to `/tokens/` and click the **envelope icon** next to each operator. This copies a ready-made email to your clipboard — paste it into Outlook (or your email client) and send.

The email contains:
- The operator's unique access code
- A link to the BORS login page (`/access/`)

### Step 4 — Monitor submissions

The Token Manager shows each operator's return status: **Draft** (started, not submitted) or **Submitted**.

Check back periodically and chase operators who have not submitted by the deadline.

### Step 5 — Download all submissions

Once the collection period closes, go to `/tokens/` and use the download buttons in the top-right corner:

| Button | File | Contents |
|--------|------|----------|
| Download All (Excel) | `BORS_All_Operators.xlsx` | 6 sheets: General, Licences, Emissions, Vehicle Route Usage, Accessibility, Declarations |
| Download All (JSON) | `BORS_All_Operators.json` | Full nested data for all operators |

Both files include all operators regardless of submission status (draft returns are included).

---

## Seeding operator data

### What gets pre-filled

| Panel | Pre-filled from seed | Operator fills in |
|-------|---------------------|-------------------|
| Step 2 Licences | Route No | All Y/N columns, passenger numbers, km, PVR |
| Step 3 Emissions | RES ID, Reg No, Make, Model, Transmission, Engine Type, Seats on Record | Y/N fields, fuel type, Euro standard, route usage % |

### Clearing seed data

Seed data is stored in the database. To remove it, use the Django admin at `/admin/` → **Seed Licences** or **Seed Vehicles**.

Removing seed data does not affect returns that have already been started — operator-entered data is separate.

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
| `/staff/export/excel/` | NTA staff | Bulk Excel download |
| `/staff/export/json/` | NTA staff | Bulk JSON download |
| `/access/` | Operators | Token login page |

### Management commands

```bash
# Import seed data from the seed_data/ folder
python manage.py ingest_seed

# Import from a specific file
python manage.py ingest_seed --file seed_data/2026_seed.xlsx

# Apply all database migrations (run after code updates)
python manage.py migrate

# Create a new staff account
python manage.py createsuperuser
```

### Data year

The data year is set by the operator in Step 1 (General). There is no system-wide year setting — each return carries its own year. This means the same operator can have multiple returns for different years in the database simultaneously.

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
