# OPELSS API Documentation

Reference for every HTTP route exposed by OPELSS, the roles permitted to call it, its
parameters and its responses.

OPELSS is a server-rendered Flask application rather than a REST API — most routes return
HTML or a redirect. A subset of routes additionally accept and return **JSON** so the UI can
submit forms without a page reload; those are marked **JSON** and documented in
[JSON endpoints](#json-endpoints).

- **Base URL (production):** the Azure App Service host for the `opelss` web app
- **Base URL (local):** `http://localhost:5000`

---

## Conventions

### Authentication

Session-cookie based, via Flask-Login. Unauthenticated requests to a protected route are
redirected to `/login`.

### Authorisation

| Marker | Meaning |
| --- | --- |
| 🌐 **Public** | No login required. |
| 🔒 **Any** | Any authenticated user. |
| **Admin** | Admins only. |
| **HQ Trainee** | HQ Trainees only. |
| **Lab Trainee** | Lab Trainees only. |
| **own lab** | Lab Trainees are restricted to their `assigned_lab_id`; Admin and HQ Trainee see all labs. |

Roles are enforced either by the `role_required(...)` decorator (`app/utils.py`) or by an
explicit check inside the view. A failed authorisation returns **403 Forbidden**.

### CSRF

All `POST` routes require a CSRF token (Flask-WTF). Send it either as a `csrf_token` form
field or an `X-CSRFToken` header for JSON requests.

### Responses

| Type | Behaviour |
| --- | --- |
| HTML | Rendered page. |
| Redirect | `302` back to the module's index, with a flash message shown as a toast. |
| JSON | `{"success": true/false, "message": "..."}` plus route-specific fields. |
| File | `.xlsx` or `.pdf` as an attachment (`Content-Disposition: attachment`). |

### Status codes

| Code | Meaning |
| --- | --- |
| `200` | Success. |
| `302` | Redirect (usually after a successful `POST`). |
| `400` | Validation failure (JSON requests). |
| `403` | Role or lab-scope not permitted. |
| `404` | Record not found. |
| `405` | Method not allowed. |

---

## Authentication (`/`)

| Method | Path | Access | Description |
| --- | --- | --- | --- |
| `GET` | `/` | 🌐 Public | Landing page: active announcements carousel and the enquiry tracking form. |
| `GET`, `POST` | `/login` | 🌐 Public | Staff login. `POST` accepts `email`, `password`, and optional `latitude`/`longitude` for geolocation. |
| `GET` | `/logout` | 🔒 Any | Ends the session and redirects to the landing page. |
| `GET`, `POST` | `/reset-password` | 🔒 Any | Change the signed-in user's own password. |

---

## Dashboard (`/dashboard`)

| Method | Path | Access | Description |
| --- | --- | --- | --- |
| `GET` | `/dashboard/` | 🔒 Any | Role-specific dashboard. Admin and HQ Trainee get cross-lab metrics; Lab Trainees get their own lab. Returns `403` for an unrecognised role. |

---

## Attendance (`/attendance`)

> **Note:** these routes are guarded by login only — there is **no role check**. What gates them
> in practice is `assigned_lab`: a user without an assigned lab cannot clock in or out. They are
> intended for Lab Trainees.

| Method | Path | Access | Description |
| --- | --- | --- | --- |
| `GET` | `/attendance/` | 🔒 Any | Attendance overview and clock-in/out controls for the signed-in user. |
| `POST` | `/attendance/clock-in` | 🔒 Any (needs assigned lab) | Records a clock-in. Requires `latitude` and `longitude`; rejected if outside the lab's configured radius. |
| `POST` | `/attendance/clock-out` | 🔒 Any (needs assigned lab) | Records a clock-out. Requires `latitude`/`longitude`, plus an early-departure reason when leaving before the scheduled end. |
| `GET` | `/attendance/export-timesheet` | 🔒 Any | Monthly timesheet as a **PDF** attachment. |

Times are stored in **South African Standard Time (SAST)**.

---

## Assets (`/assets`)

| Method | Path | Access | Description |
| --- | --- | --- | --- |
| `GET` | `/assets/` | 🔒 Any — **own lab** | Asset register. Query filters: `category`, `status`, `lab_id`, `province_id` (lab/province for Admin and HQ Trainee). |
| `POST` | `/assets/create` | 🔒 Any — **own lab** | Create an asset. **JSON** capable. |
| `POST` | `/assets/<asset_id>/update` | 🔒 Any — **own lab** | Update an asset. |
| `POST` | `/assets/<asset_id>/delete` | 🔒 Any — **own lab** | Delete an asset. |
| `GET` | `/assets/export` | **Admin**, **HQ Trainee** | Excel export honouring `category`, `status`, `lab_id`, `province_id`. Returns `assets_export.xlsx`. |

**Asset fields:** `asset_name`, `category`, `serial_number`, `status`, `lab_id`.

---

## Visitors (`/visitors`)

| Method | Path | Access | Description |
| --- | --- | --- | --- |
| `GET` | `/visitors/` | 🔒 Any — **own lab** | Visitor log. Query filters: `category`, `date_from`, `date_to`, `lab_id`, `province_id`. |
| `POST` | `/visitors/create` | 🔒 Any — **own lab** | Log a visitor. **JSON** capable. |
| `POST` | `/visitors/<visitor_id>/update` | 🔒 Any — **own lab** | Update a visitor record. |
| `POST` | `/visitors/<visitor_id>/delete` | 🔒 Any — **own lab** | Delete a visitor record. |
| `GET` | `/visitors/export` | **Admin**, **HQ Trainee** | Excel export honouring the same filters. |

**Visitor fields:** `visitor_name`, `category`, `student_number`, `cellphone`, `purpose`, `visit_date`, `lab_id`.

---

## Programmes (`/programmes`)

| Method | Path | Access | Description |
| --- | --- | --- | --- |
| `GET` | `/programmes/` | 🔒 Any — **own lab** | Programme register. Query filters: `date_from`, `date_to`, `lab_id`, `province_id`, `facilitator_id`. |
| `POST` | `/programmes/create` | 🔒 Any — **own lab** | Log a programme. **JSON** capable. |
| `POST` | `/programmes/<programme_id>/update` | 🔒 Any — **own lab** | Update a programme, including its facilitators. |
| `POST` | `/programmes/<programme_id>/delete` | 🔒 Any — **own lab** | Delete a programme. |
| `GET` | `/programmes/export` | **Admin**, **HQ Trainee** | Excel export honouring `date_from`, `date_to`, `lab_id`, `province_id`, `facilitator_id`. Returns `programmes_export.xlsx`. |

**Programme fields:** `title`, `objective`, `target_audience`, `attendance_count`,
`activities_done`, `date`, `start_time`, `end_time`, `lab_id`, `facilitators` (repeated field —
one value per selected facilitator).

**Facilitators.** `facilitators` is a many-to-many link to users, recording *who ran* the
programme. It is distinct from `created_by`, which records who captured the record. At least
one facilitator is required.

**Time format.** `start_time` and `end_time` accept `HH:MM` or `HH:MM:SS`.

---

## Enquiries (`/enquiries`)

| Method | Path | Access | Description |
| --- | --- | --- | --- |
| `GET` | `/enquiries/` | 🔒 Any — **own lab** | Enquiry list. Lab Trainees see their own lab's enquiries. |
| `POST` | `/enquiries/create` | **Lab Trainee** | Raise and escalate an enquiry; a tracking number is generated. **JSON** capable. |
| `POST` | `/enquiries/<enquiry_id>/edit` | **Lab Trainee** — own lab | Edit an enquiry. Only while status is `Open`. |
| `POST` | `/enquiries/<enquiry_id>/delete` | **Lab Trainee** — own lab | Delete an enquiry. Only while status is `Open`. |
| `POST` | `/enquiries/<enquiry_id>/assign` | **Admin** | Assign an enquiry to an HQ Trainee. |
| `POST` | `/enquiries/<enquiry_id>/reassign` | **Admin** | Reassign to a different handler. |
| `POST` | `/enquiries/<enquiry_id>/start` | **Admin**, **HQ Trainee** | Mark as in progress. HQ Trainees must be the assignee. |
| `POST` | `/enquiries/<enquiry_id>/resolve` | **Admin**, **HQ Trainee** | Mark as resolved. HQ Trainees must be the assignee. |
| `POST` | `/enquiries/<enquiry_id>/not-resolved` | **Admin**, **HQ Trainee** | Mark as not resolved, with a reason. HQ Trainees must be the assignee. |
| `POST` | `/enquiries/<enquiry_id>/close` | **Admin** | Close an enquiry. |
| `POST` | `/enquiries/<enquiry_id>/reopen` | **Admin** | Reopen a closed enquiry. |
| `GET`, `POST` | `/enquiries/track` | 🌐 **Public** | Public status tracker — a student submits a `tracking_number` and sees the status. No login. |

**Enquiry fields:** `student_name`, `student_number`, `category`, `description`,
`escalation_reason`, `lab_id`.

**Workflow.** `Open → Assigned → In Progress → Resolved / Not Resolved → Closed`, with a
timestamp captured at each transition (`escalated_at`, `assigned_at`, `in_progress_at`,
`resolved_at`, `closed_at`).

---

## Announcements (`/announcements`)

| Method | Path | Access | Description |
| --- | --- | --- | --- |
| `GET` | `/announcements/manage` | **Admin**, **HQ Trainee** | Manage announcements. |
| `POST` | `/announcements/create` | **Admin**, **HQ Trainee** | Create an announcement with an expiry date and optional poster image. |
| `GET` | `/announcements/poster/<filename>` | 🌐 Public | Serve an uploaded poster image. |

Announcements appear on the public landing page until their `expiry_date` passes.

---

## Reports (`/reports`)

| Method | Path | Access | Description |
| --- | --- | --- | --- |
| `GET` | `/reports/` | **Admin**, **HQ Trainee** | Report export page. |
| `GET` | `/reports/export/<report_type>` | **Admin**, **HQ Trainee** | Generate an Excel report. Returns `<report_type>_report.xlsx`. |

**`report_type`:** `attendance`, `assets`, `visitors`, `programmes`, `labs`, `provinces`.
Any other value returns an error.

**Query parameters:** `province_id`, `lab_id`, `start_date`, `end_date`.

Each workbook contains a **Raw Data** sheet and a **Summary** sheet.

---

## Administration (`/admin`)

All routes require **Admin**.

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/admin/` | Administration dashboard — users, labs and provinces. |
| `POST` | `/admin/users` | Create a user. Returns a generated temporary password. **JSON** capable. |
| `POST` | `/admin/users/<user_id>/update` | Update a user's details, role or assigned lab. |
| `POST` | `/admin/users/<user_id>/delete` | Delete a user. |
| `POST` | `/admin/users/<user_id>/reset-password` | Reset a password; returns a new temporary password. **JSON** capable. |
| `POST` | `/admin/labs` | Create a lab, including geo-coordinates and clock-in radius. |
| `POST` | `/admin/labs/<lab_id>/update` | Update a lab. |
| `POST` | `/admin/labs/<lab_id>/delete` | Delete a lab. |
| `POST` | `/admin/provinces` | Create a province. |
| `POST` | `/admin/provinces/<province_id>/update` | Update a province. |
| `POST` | `/admin/provinces/<province_id>/delete` | Delete a province. |

**User fields:** `full_name`, `staff_number`, `email`, `role`, `assigned_lab_id`, `active`.
**Lab fields:** `name`, `province_id`, `latitude`, `longitude`, `radius_meters`.

---

## Audit (`/audit`)

| Method | Path | Access | Description |
| --- | --- | --- | --- |
| `GET` | `/audit/` | **Admin** | Audit log of create/update/delete activity. Filterable by date. |

Each entry records the actor, their role, the action, the entity type and label, and a
SAST timestamp.

---

## JSON endpoints

Routes marked **JSON** accept `Content-Type: application/json` and return JSON instead of a
redirect, so the UI can update without a full page reload.

### Request

```http
POST /programmes/create
Content-Type: application/json
X-CSRFToken: <token>
```

```json
{
  "title": "Career Expo",
  "objective": "Expose students to career opportunities",
  "target_audience": "Final year students",
  "attendance_count": "42",
  "activities_done": "Talks and CV workshops",
  "date": "2026-06-12",
  "start_time": "09:00",
  "end_time": "12:00",
  "lab_id": "1",
  "facilitators": ["2", "3"]
}
```

> Multi-value fields such as `facilitators` are sent as an **array**.

### Success

```json
{
  "success": true,
  "message": "Programme logged successfully.",
  "row_html": "<tr data-id=\"5\" ...>...</tr>",
  "reload": false,
  "reset": true
}
```

| Field | Meaning |
| --- | --- |
| `success` | Whether the operation succeeded. |
| `message` | Text shown to the user as a toast. |
| `row_html` | Rendered table row, inserted into the page without a reload. |
| `reload` | Whether the client should reload the page. |
| `reset` | Whether the form should be cleared. |
| `redirect` | Where to navigate next, when present. |
| `temporary_password` | Returned by the admin user-create and password-reset routes. |

### Failure

```json
{
  "success": false,
  "message": "Unable to log programme. title: This field is required."
}
```

Returned with **400 Bad Request**.

---

## Related documentation

- [Permissions matrix](permissions-matrix.md) — roles and their permissions.
- [ERD](erd.md) — database schema.
- [Project README](../README.md) — setup and deployment.
