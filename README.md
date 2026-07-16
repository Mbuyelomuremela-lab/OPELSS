# OPELSS

**OPELSS** (OAU E-Learning Lab Support System) is the web application the ODeL Acceleration Unit
uses to run its network of e-learning labs. Lab trainees clock in, log visitors, track equipment,
record community programmes and escalate student enquiries; HQ sees all of it live and exports
reports in one click, instead of consolidating spreadsheets by hand every month.

Flask · PostgreSQL · Bootstrap 5 · hosted on Azure.

---

## Run it locally

You need **Python 3.11.8** and **Git**. Nothing else — it defaults to a local SQLite database,
so there is no database server to install.

```bash
git clone git@github.com:Mbuyelomuremela-lab/OPELSS.git
cd OPELSS

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt

echo "SECRET_KEY=dev-secret-not-for-production" > .env

python run.py
```

Open <http://localhost:5000>.

That's it. On first run the app creates `instance/app.db` and seeds it, so you get a working
system with data already in it — no migration or fixture step needed.

### Log in

The seed creates one administrator:

| Email | Password |
| --- | --- |
| `admin@opelss.com` | `Admin@123` |

Log in with that and you have the run of the system.

> **Change this password on anything other than your own machine.** The seed runs on every
> startup and creates this account if it is missing — including in production.

### ⚠️ You cannot log in as a Lab Trainee without faking your location

This trips everyone up. Lab Trainee login is **geo-fenced**: the browser sends your coordinates
and the server rejects the login unless you are within the lab's radius. The seeded **"Main Lab"
sits at latitude 0, longitude 0** — a spot in the Atlantic Ocean — so a real browser will never
be close enough, and you will just be told you must be inside your lab radius.

Pick whichever you prefer:

**Option A — move the lab to you** (persists, best for ongoing work)

Log in as admin → **Admin** → **Labs** → edit **Main Lab** → set its latitude/longitude to your
own, or set `radius_meters` to something enormous.

**Option B — fake your location in the browser** (nothing to change in the app)

Chrome DevTools → ⋮ → More tools → **Sensors** → **Location** → *Other…* → enter `0`, `0`.

**Option C — move the lab to you from the shell**

```bash
python3 -c "
from run import app
from app.extensions import db
from app.models.lab import Lab
with app.app_context():
    lab = Lab.query.filter_by(name='Main Lab').first()
    lab.radius_meters = 20000000      # effectively the whole planet
    db.session.commit()
    print('Main Lab radius widened — any location will now clock in')
"
```

Admin and HQ Trainee logins are **not** geo-fenced, so you only hit this when testing the Lab
Trainee experience.

### What the seed gives you

| | |
| --- | --- |
| Province | Headquarters |
| Lab | Main Lab — at `0, 0`, radius 1000 m |
| User | `admin@opelss.com` / `Admin@123` (Admin) |

Everything else — more labs, users, assets, visitors, programmes — you create through the UI as
an admin.

### Run the tests

```bash
python -m unittest discover tests
```

There is one test, covering database initialisation. `pytest` is not a dependency, so use
`unittest`.

### Useful environment variables

Only `SECRET_KEY` really matters locally. Everything else has a working default.

| Variable | Default | What it does |
| --- | --- | --- |
| `SECRET_KEY` | `change-this-secret-key` | Signs sessions and CSRF tokens. Set it. |
| `DATABASE_URL` | SQLite at `instance/app.db` | Point at PostgreSQL to use one. `postgres://` is rewritten to `postgresql://` for you. |
| `FLASK_DEBUG` | `0` | `1` for the debugger and auto-reload. |
| `PORT` | `5000` | Port for `python run.py`. |
| `FLASK_ENV` | `production` | `development` relaxes secure-cookie enforcement. |
| `UPLOAD_FOLDER` | `uploads/` | Where announcement posters are stored. |

### Things worth knowing before you change code

- **Times are SAST, not UTC.** The server runs in UTC but everyone using it is in South Africa.
  Always use `sast_now()` / `sast_today()` from `app/utils.py` — never `datetime.now()`,
  `utcnow()` or `date.today()`.
- **The database is created two ways.** `db.create_all()` runs on every startup and creates any
  *missing tables*, which is why a fresh clone just works. It cannot alter existing tables, so
  **adding a column to an existing table needs a migration**:
  ```bash
  flask --app run db migrate -m "what you changed"
  flask --app run db upgrade
  ```
  Adding a whole new table needs no migration to work locally — but write one anyway so
  production stays reproducible.
- **Templates are cached.** `python run.py` without `FLASK_DEBUG=1` caches compiled templates,
  so edits to `.html` will not appear until you restart. Set `FLASK_DEBUG=1` to avoid this.
- **Lab Trainees only ever see their own lab.** Most modules filter on `assigned_lab_id`. If a
  record "disappears", check which lab the logged-in user belongs to.

---

## How the system fits together

Each feature is a Flask blueprint under `app/`, with its own routes, forms, services and
templates. They all follow the same shape, so once you have read one you can read them all.

| Blueprint | URL | What it does |
| --- | --- | --- |
| `auth` | `/` | Landing page, login (geo-fenced for Lab Trainees), logout. |
| `dashboard` | `/dashboard` | A different dashboard per role. |
| `attendance` | `/attendance` | Geolocation clock-in/out, PDF timesheets. |
| `assets` | `/assets` | Equipment register per lab. |
| `visitors` | `/visitors` | Visitor log per lab. |
| `programmes` | `/programmes` | Community programmes, and who facilitated them. |
| `enquiries` | `/enquiries` | Student enquiries, plus a public tracker needing no login. |
| `announcements` | `/announcements` | Notices on the public landing page. |
| `reports` | `/reports` | One-click Excel exports. |
| `admin` | `/admin` | Users, labs, provinces. |
| `audit` | `/audit` | Who created, changed or deleted what. |

### The three roles, briefly

- **Lab Trainee** — runs one lab. Sees only their own lab's data.
- **HQ Trainee** — sees every lab. Handles enquiries, announcements and reporting.
- **Admin** — everything, plus users, labs and the audit log.

Plus the **public**: students track an enquiry by reference number and read announcements without
an account.

→ Exactly who can do what: **[docs/permissions-matrix.md](docs/permissions-matrix.md)**

### Where the data lives

Everything hangs off **labs**. Assets, visitors, programmes, enquiries and attendance all carry a
`lab_id`, which is what makes "Lab Trainees see only their own lab" possible.

→ Full schema and diagram: **[docs/erd.md](docs/erd.md)**

---

## Deployment

Push to `main` and it deploys itself — [`.github/workflows/main_opelss.yml`](.github/workflows/main_opelss.yml)
builds and ships to the `opelss` Azure Web App.

The **startup command**, set in the Azure Portal (Configuration → Startup Command), applies any
pending migrations before booting the server:

```bash
flask --app run db upgrade && gunicorn wsgi:app
```

So a migration you commit is applied automatically on the next deploy — you do not have to run
anything by hand.

Production settings live in Azure Portal → Configuration → Application settings:

| Variable | Value |
| --- | --- |
| `SECRET_KEY` | A long random secret. |
| `DATABASE_URL` | The Azure PostgreSQL connection string, with `?sslmode=require`. |
| `FLASK_ENV` | `production` |

---

## Project layout

```
app/
├── __init__.py          # app factory, blueprint registration, seed_data()
├── models/              # SQLAlchemy models — one file per table
├── utils.py             # role_required decorator, sast_now()/sast_today()
├── extensions.py        # db, login_manager
├── templates/           # Jinja2 — base.html plus one folder per blueprint
├── static/              # css/app.css, js/main.js
└── <blueprint>/         # routes.py, forms.py, services.py per feature
config.py                # Config / DevelopmentConfig / ProductionConfig
run.py                   # local entry point  → python run.py
wsgi.py                  # production entry point → gunicorn wsgi:app
migrations/              # Alembic
docs/                    # documentation
```

Business logic lives in each blueprint's `services.py`, not in `routes.py` — routes stay thin and
handle HTTP, services do the work and are the part worth testing.

---

## Documentation

| | |
| --- | --- |
| [Business case](docs/business-case.docx) | Why OPELSS exists, scope, costs, schedule. For stakeholders. |
| [API documentation](docs/api-documentation.md) | Every route, who may call it, what it takes and returns. |
| [ERD](docs/erd.md) | Database schema and relationships. |
| [Permissions matrix](docs/permissions-matrix.md) | What each role may do. |
| [Training manuals](docs/manuals/) | End-user guides, one per role. |
