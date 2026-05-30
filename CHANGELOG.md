# BORS — Release Notes

---

## v1.2.0 — 2026-05-30

### Test Mode
- Operators can be flagged as **test accounts** via the flask icon in the Token Manager.
- A **TEST** badge appears in the token table and on the operator's own return page.
- New management command to wipe test data without touching real submissions:
  ```bash
  python manage.py clear_submissions --test-only --confirm
  python manage.py clear_submissions --all --confirm
  ```

### Year Locks
- Staff can lock a collection year at `/staff/locks/` to prevent operators from editing or submitting returns once the collection period closes.
- Locked returns become fully **read-only** in the browser — all form fields are disabled, save buttons are hidden.
- A prominent amber banner is shown on every step page and the operator index when their year is locked.
- Years can be unlocked at any time from the same page.

### Year-scoped Seed Data
- Seed data (routes and vehicles) is now tied to a specific **data year**.
- The seed import form at `/staff/seed-import/` requires a year to be selected before uploading.
- The current seed data table can be filtered by year.
- `ingest_seed` management command now requires `--year`:
  ```bash
  python manage.py ingest_seed --year 2025
  ```

---

## v1.1.0 — 2026-05-29

### Staff Admin Shell
- Added NTA staff portal pages: Token Manager (`/tokens/`), Seed Data Import (`/staff/seed-import/`).
- Bulk Excel and JSON exports of all operator submissions.
- Seed data pre-population: staff upload routes and vehicles per operator; data is applied on the operator's first visit to Step 2 or Step 3.
- Token management: create operators, copy ready-made access emails, revoke/restore access, regenerate tokens.

### General Fixes
- Render deployment fixes (static files, build pipeline).
- Template and form corrections across all five return steps.

---

## v1.0.0 — 2026-05-21

### Initial Release
- Five-step operator return form: General, Licences, Emissions, Accessibility, Declaration.
- Token-based operator login (no passwords — staff email a unique access code per operator).
- Draft auto-save across all steps; final submission locks the return as **Submitted**.
- Per-operator Excel export available after submission.
- Django admin for direct data access.
- Deployed on Render with PostgreSQL.
