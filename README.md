# OPELSS

OPELSS is a modular enterprise Flask application for the OAU-PID e-Lab Support System.

## Features

- Role-based access control for Admin, HQ Trainee, and Lab Trainee
- Geolocation-protected lab trainee login
- Attendance clock-in/out with audit tracking and PDF export
- Asset, visitor, enquiry, programme, and announcement management
- Excel exports using OpenPyXL
- Report generation for attendance, assets, visitors, programmes, labs, and provinces
- Responsive Bootstrap 5 UI
- Production deployment support via Gunicorn and Render

## Setup

1. Copy `.env.example` to `.env` and update values
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize the database:
   ```bash
   flask db init
   flask db migrate -m "Initial schema"
   flask db upgrade
   ```
4. Run the app locally:
   ```bash
   python run.py
   ```

## Deployment

- Use `Procfile` with `gunicorn wsgi:app`
- Render support is configured in `.render.yaml`
- Use `runtime.txt` to lock the Python version on Render
- Add required production environment variables in Render: `DATABASE_URL`, `SECRET_KEY`, `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `OPELSS_ADMIN_EMAIL`

## Notes

- Lab Trainee login requires browser geolocation access
- Admin can create users and manage labs, provinces, and announcements
- Public landing page includes an announcements carousel and enquiry tracking form
