# OPELSS

**OPELSS** (OAU E-Learning Lab Support System) is a role-based Flask web application that
centralises the day-to-day operations of the ODeL Acceleration Unit's network of e-learning
labs — attendance, assets, visitors, programmes, enquiries, announcements and reporting — in
one place, with data visible to HQ in real time instead of being consolidated by hand each month.

📚 Full documentation lives in [`docs/`](docs/) — including the [business case](docs/business-case.docx),
[API reference](docs/api-documentation.md), [ERD](docs/erd.md), [permissions matrix](docs/permissions-matrix.md),
and the [training manuals](docs/manuals/).

---

## Features

**Attendance**
- Geolocation-enforced clock-in/out — a trainee can only clock in within a configured radius of their assigned lab.
- Early-departure reason capture.
- Monthly PDF timesheet export.
- Times recorded in South African Standard Time (SAST).

**Assets**
- Register lab equipment by name, category, serial/tag number and status.
- Filter by category, status, lab and province.
- Export to Excel with the on-screen filters applied.

**Visitors**
- Log each visitor with name, category, student number, cellphone, purpose and date.
- Filter by category, date range, lab and province.
- Export to Excel with filters applied.

**Programmes**
- Log community programmes with objective, target audience, attendance, activities, date and times.
- **Facilitators audit trail** — records every person who ran a programme (separate from whoever captured it).
- Filter by date range, lab, province and facilitator.
- Export to Excel with filters applied.

**Enquiries**
- Capture and escalate student enquiries with an auto-generated tracking number.
- Workflow states with timestamps (escalated, assigned, in progress, resolved, closed).
- **Public tracker** — students check status by reference number, no login required.

**Announcements**
- Posted by Admin with an expiry date; shown on the public landing page until they expire.

**Reports**
- One-click Excel export by report type (attendance, assets, visitors, programmes, labs, provinces),
  filtered by province and lab.

**Administration**
- Manage users, roles, labs, provinces and lab geo-coordinates.
- **Audit log** of create/update/delete activity across the system.

---

## Roles

OPELSS has three authenticated roles plus unauthenticated public access.

| Role | Scope of data | Primary purpose |
| --- | --- | --- |
| **Lab Trainee** | Their assigned lab only | Run the day-to-day operations of one lab. |
| **HQ Trainee** | All labs, all provinces | Oversee and support labs from HQ; reporting. |
| **Admin** | Everything | Full control, including user and lab administration. |
| **Public** (no login) | Public pages only | Students tracking an enquiry or reading announcements. |

### What each role can do

| Function | Lab Trainee | HQ Trainee | Admin | Public |
| --- | :---: | :---: | :---: | :---: |
| Clock in / out (geolocation) | ✅ own lab | ⚠️ any user with an assigned lab | ⚠️ any user with an assigned lab | — |
| Export own timesheet (PDF) | ✅ | ✅ | ✅ | — |
| Assets — add / edit / delete | ✅ own lab | ✅ all | ✅ all | — |
| Visitors — log / edit / delete | ✅ own lab | ✅ all | ✅ all | — |
| Programmes — log / edit / delete | ✅ own lab | ✅ all | ✅ all | — |
| Excel export (assets/visitors/programmes) | — | ✅ | ✅ | — |
| Enquiries — raise / escalate | ✅ | — | — | — |
| Enquiries — work (start / resolve) | — | ✅ assigned to them | ✅ any | — |
| Enquiries — assign / close / reopen | — | — | ✅ | — |
| Track an enquiry by reference number | — | — | — | ✅ |
| Reports — generate exports | — | ✅ | ✅ | — |
| Announcements — create / manage | — | ✅ | ✅ | 👁 view |
| Users, labs, provinces — administer | — | — | ✅ | — |
| Audit log | — | — | ✅ | — |

> ⚠️ Attendance routes are guarded by login only — no role check. Having an `assigned_lab` is
> what gates them in practice. See [docs/permissions-matrix.md](docs/permissions-matrix.md).

> A precise, route-by-route breakdown is in [docs/permissions-matrix.md](docs/permissions-matrix.md).

---

## Tech stack

| Layer | Technology |
| --- | --- |
| Language | Python 3.11.8 |
| Framework | Flask (blueprint-per-module) |
| ORM / migrations | SQLAlchemy, Flask-Migrate (Alembic) |
| Auth | Flask-Login, Flask-WTF (CSRF) |
| Database | PostgreSQL in production, SQLite for local development |
| Frontend | Jinja2 templates, Bootstrap 5, vanilla JS |
| Exports | OpenPyXL (Excel), ReportLab (PDF) |
| Server | Gunicorn |
| Hosting | Azure App Service + Azure Database for PostgreSQL |

---

## Getting started

### Prerequisites

- Python **3.11.8** (see [`runtime.txt`](runtime.txt))
- Git

### Installation

```bash
# 1. Clone the repository
git clone git@github.com:Mbuyelomuremela-lab/OPELSS.git
cd OPELSS

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```bash
# Required — used to sign sessions and CSRF tokens. Use a long random value.
SECRET_KEY=your-secret-key-here

# Optional — omit to use a local SQLite database at instance/app.db
DATABASE_URL=postgresql://user:password@host:5432/dbname?sslmode=require

# Optional
UPLOAD_FOLDER=uploads        # where announcement images are stored
FLASK_ENV=development        # "production" enables secure cookies
FLASK_DEBUG=1                # enables the Flask debugger and reloader
PORT=5000                    # port for `python run.py`
```

| Variable | Required | Default | Purpose |
| --- | :---: | --- | --- |
| `SECRET_KEY` | ✅ | `change-this-secret-key` | Session and CSRF signing. **Must** be set in production. |
| `DATABASE_URL` | — | SQLite at `instance/app.db` | Database connection. `postgres://` is normalised to `postgresql://` automatically. |
| `UPLOAD_FOLDER` | — | `uploads/` | Announcement image uploads. |
| `FLASK_ENV` | — | `production` | Set to `development` locally to relax secure-cookie enforcement. |
| `FLASK_DEBUG` | — | `0` | Set to `1` for the debugger and auto-reload. |
| `PORT` | — | `5000` | Port used by `python run.py`. |

### Database setup

Migrations already exist in [`migrations/`](migrations/), so apply them rather than initialising:

```bash
flask --app run db upgrade
```

> The app also runs `db.create_all()` on startup, so a fresh SQLite database is created
> automatically on first run. Migrations matter when **adding columns to existing tables**,
> which `create_all()` cannot do.

### Run it

```bash
python run.py
```

The app is served at <http://localhost:5000> (or `PORT`).

On first run a default administrator is seeded:

| Email | Password |
| --- | --- |
| `admin@opelss.com` | `Admin@123` |

> ⚠️ **Change this password immediately** on any deployment reachable by anyone else.
> The seed only creates the account if it does not already exist.

Lab Trainee login requires the browser to grant **geolocation** access.

---

## Deployment

OPELSS deploys to **Azure App Service**.

- **Trigger** — pushing to `main` runs [`.github/workflows/main_opelss.yml`](.github/workflows/main_opelss.yml),
  which builds and deploys to the `opelss` Azure Web App.
- **Startup command** (configured in the Azure Portal → Configuration → Startup Command) applies
  pending migrations before starting the server:
  ```bash
  flask --app run db upgrade && gunicorn wsgi:app
  ```
- **Process definition** — [`Procfile`](Procfile): `gunicorn wsgi:app`
- **Python version** — pinned by [`runtime.txt`](runtime.txt).

### Production environment variables

Set these in Azure Portal → Configuration → Application settings:

| Variable | Value |
| --- | --- |
| `SECRET_KEY` | A long, random secret. |
| `DATABASE_URL` | The Azure PostgreSQL connection string (`?sslmode=require`). |
| `FLASK_ENV` | `production` |

---

## Project structure

```
OPELSS/
├── app/
│   ├── __init__.py          # app factory, blueprint registration, seed data
│   ├── models/              # SQLAlchemy models
│   ├── auth/                # login, logout, password change
│   ├── dashboard/           # role-specific dashboards
│   ├── attendance/          # geolocation clock-in/out, timesheets
│   ├── assets/              # asset register
│   ├── visitors/            # visitor log
│   ├── programmes/          # programme log + facilitators
│   ├── enquiries/           # enquiry workflow + public tracker
│   ├── announcements/       # announcements
│   ├── reports/             # Excel report exports
│   ├── admin/               # users, labs, provinces
│   ├── audit/               # audit log
│   ├── templates/           # Jinja2 templates
│   ├── static/              # CSS, JS, images
│   └── utils.py             # role decorators, SAST time helpers
├── docs/                    # project documentation
├── migrations/              # Alembic migrations
├── tests/
├── config.py                # configuration classes
├── run.py                   # local entry point
├── wsgi.py                  # WSGI entry point (Gunicorn)
└── requirements.txt
```

### Modules and URL prefixes

| Blueprint | Prefix | Purpose |
| --- | --- | --- |
| `auth` | `/` | Landing page, login, logout. |
| `dashboard` | `/dashboard` | Role-specific dashboard. |
| `attendance` | `/attendance` | Clock in/out, timesheets. |
| `assets` | `/assets` | Asset register. |
| `visitors` | `/visitors` | Visitor log. |
| `programmes` | `/programmes` | Programme log and facilitators. |
| `enquiries` | `/enquiries` | Enquiry workflow and public tracker. |
| `announcements` | `/announcements` | Announcement management. |
| `reports` | `/reports` | Report exports. |
| `admin` | `/admin` | User, lab and province administration. |
| `audit` | `/audit` | Audit log. |

---

## Conventions

- **Times are SAST.** Use `sast_now()` / `sast_today()` from `app/utils.py` for the current
  time — never `datetime.now()`, `utcnow()` or `date.today()`, because the server runs in UTC
  while users are in South Africa.
- **Roles** are enforced with the `role_required(...)` decorator in `app/utils.py`; Lab Trainees
  are additionally scoped to `assigned_lab_id` within each module.
