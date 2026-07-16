# OPELSS Routes

Every URL the application answers on, who is allowed to call it, and what comes back.

---

## First, the thing that surprises people

**OPELSS is not a REST API.** It is a server-rendered Flask app. Most routes return an HTML page
or a redirect, not JSON. There is no token auth, no `/api/v1/` prefix, and no versioning.

What it *does* have is a handful of routes that answer **either** HTML **or** JSON depending on
how you ask, so the UI can submit a form without reloading the page. Those are marked **JSON**
below and explained in [Talking JSON](#talking-json).

So if you came looking for an API to integrate against: it isn't one. If you came to find out
what happens when a button is clicked: read on.

---

## How every route works

Three things are true of nearly all of them.

**1. You are identified by a session cookie.** Flask-Login. No token. Not logged in and you hit
a protected route? You are bounced to `/login`.

**2. Every POST needs a CSRF token.** Either a `csrf_token` form field, or an `X-CSRFToken`
header if you are sending JSON. Without it you get a 400.

**3. A successful POST redirects; it does not return a body.** The classic form pattern: POST,
then `302` back to the module's index, with a flash message that renders as a toast. The JSON
routes are the exception.

### Reading the access column

| | |
| --- | --- |
| 🌐 | Anyone. No login. |
| 🔒 | Any logged-in user. |
| 🔸 | Any logged-in user, **but Lab Trainees only see their own lab.** |
| 👑 | Admin only. |
| 🗂️👑 | HQ Trainee and Admin. |
| 🔧 | Lab Trainee only. |

Anything you are not allowed to do returns **403**. Full reasoning behind these:
[permissions matrix](permissions-matrix.md).

---

## Getting in and out

| | Route | Who | What happens |
| --- | --- | :---: | --- |
| `GET` | `/` | 🌐 | The public landing page — announcements carousel and the enquiry tracker. |
| `GET` `POST` | `/login` | 🌐 | Sign in. Posts `email`, `password`, and `latitude`/`longitude`. |
| `GET` | `/logout` | 🔒 | Ends the session. |
| `GET` `POST` | `/reset-password` | 🔒 | Change your own password. |
| `GET` | `/dashboard/` | 🔒 | A different dashboard per role. An unrecognised role gets a 403. |

> **Why does login take coordinates?** Because a **Lab Trainee** can only sign in from inside
> their lab. The server measures the distance to the lab and refuses if you are outside
> `radius_meters`. Admins and HQ Trainees are not geo-fenced, so their coordinates are ignored.

---

## Attendance

| | Route | Who | What happens |
| --- | --- | :---: | --- |
| `GET` | `/attendance/` | 🔒 | Your attendance page and clock-in/out buttons. |
| `POST` | `/attendance/clock-in` | 🔒 | Starts your day. Needs `latitude`, `longitude`. |
| `POST` | `/attendance/clock-out` | 🔒 | Ends it. Needs coordinates, plus a reason if you are leaving early. |
| `GET` | `/attendance/export-timesheet` | 🔒 | Your month as a **PDF**. |

Clock-in is rejected outside the lab's radius, exactly like login.

> ⚠️ **These have no role check** — just `login_required`. In practice what stops most people is
> not having an assigned lab. The seeded Admin *does* have one, so an Admin can clock in. See
> [permissions matrix](permissions-matrix.md#two-things-worth-a-second-look).

Times are stored in **SAST**, not UTC.

---

## The three registers

Assets, visitors and programmes are **the same page three times**. Same layout, same buttons,
same rules — only the fields differ. Learn one and you know all three.

```
/<thing>/                    the list, with filters
/<thing>/create              add one                     JSON
/<thing>/<id>/update         change one
/<thing>/<id>/delete         remove one
/<thing>/export              download the filtered list as Excel
```

| | Route | Who | Notes |
| --- | --- | :---: | --- |
| `GET` | `/assets/` `/visitors/` `/programmes/` | 🔸 | The register. Lab Trainees see only their lab. |
| `POST` | `/…/create` | 🔸 | **JSON** — the "Add" modal posts here. |
| `POST` | `/…/<id>/update` | 🔸 | |
| `POST` | `/…/<id>/delete` | 🔸 | |
| `GET` | `/…/export` | 🗂️👑 | Excel, honouring whatever filters are in the query string. |

**Export is HQ and Admin only.** A Lab Trainee can use the page but cannot download from it.

### What each one filters on

| Register | Filters |
| --- | --- |
| **Assets** | `category`, `status`, `lab_id`, `province_id` |
| **Visitors** | `category`, `date_from`, `date_to`, `lab_id`, `province_id` |
| **Programmes** | `date_from`, `date_to`, `lab_id`, `province_id`, **`facilitator_id`** |

`lab_id` and `province_id` are only shown to HQ and Admin — a Lab Trainee has nothing to filter,
they only have one lab.

### Fields

<details>
<summary><b>Assets</b></summary>

`asset_name`, `category`, `serial_number` (unique — the UNISA tag), `status`, `lab_id`

</details>

<details>
<summary><b>Visitors</b></summary>

`visitor_name`, `category`, `student_number`, `cellphone_number`, `purpose`, `visit_date`, `lab_id`

</details>

<details>
<summary><b>Programmes</b></summary>

`title`, `objective`, `target_audience`, `attendance_count`, `activities_done`, `date`,
`start_time`, `end_time`, `lab_id`, `facilitators`

**`facilitators` is repeated once per person selected** — it is a multi-select. At least one is
required. It records *who ran* the programme, which is not the same as `created_by`
(who typed it in), and that distinction is the whole point of the field.

**`start_time` / `end_time` accept both `HH:MM` and `HH:MM:SS`** — deliberately, because the
edit form pre-fills with seconds and the browser sends them back.

</details>

---

## Enquiries

The one module where the roles hand off to each other, so the routes split along those lines.

**A lab raises it:**

| | Route | Who | What happens |
| --- | --- | :---: | --- |
| `GET` | `/enquiries/` | 🔸 | The list. |
| `POST` | `/enquiries/create` | 🔧 | Raise one. A tracking number is generated. **JSON** |
| `POST` | `/enquiries/<enquiry_id>/edit` | 🔧 | Only while still `Open`. |
| `POST` | `/enquiries/<enquiry_id>/delete` | 🔧 | Only while still `Open`. |

**An admin directs it:**

| | Route | Who | What happens |
| --- | --- | :---: | --- |
| `POST` | `/enquiries/<enquiry_id>/assign` | 👑 | Hand it to an HQ Trainee. |
| `POST` | `/enquiries/<enquiry_id>/reassign` | 👑 | Hand it to someone else. |
| `POST` | `/enquiries/<enquiry_id>/close` | 👑 | Done with. |
| `POST` | `/enquiries/<enquiry_id>/reopen` | 👑 | Not done with after all. |

**HQ works it:**

| | Route | Who | What happens |
| --- | --- | :---: | --- |
| `POST` | `/enquiries/<enquiry_id>/start` | 🗂️👑 | Picking it up. |
| `POST` | `/enquiries/<enquiry_id>/resolve` | 🗂️👑 | Solved, with a note. |
| `POST` | `/enquiries/<enquiry_id>/not-resolved` | 🗂️👑 | Couldn't solve it, with a reason. |

> HQ Trainees can only act on enquiries **assigned to them**. Admins can act on any.

**The student watches:**

| | Route | Who | What happens |
| --- | --- | :---: | --- |
| `GET` `POST` | `/enquiries/track` | 🌐 | Post a `tracking_number`, see the status. **No login.** |

**Fields:** `student_name`, `student_number`, `category`, `description`, `escalation_reason`, `lab_id`

**Status:** `Open → Assigned → In Progress → Resolved`/`Not Resolved` `→ Closed`, each transition
timestamped so you can measure how long it sat at each step.

---

## Announcements

| | Route | Who | What happens |
| --- | --- | :---: | --- |
| `GET` | `/announcements/manage` | 🗂️👑 | Manage them. |
| `POST` | `/announcements/create` | 🗂️👑 | Title, message, expiry date, optional poster image. |
| `GET` | `/announcements/poster/<filename>` | 🌐 | Serves the image — public, since the landing page is. |

Announcements vanish from the landing page once `expiry_date` passes. Nobody has to tidy up.

> Note this is **HQ Trainee *and* Admin**, not Admin only.

---

## Reports

| | Route | Who | What happens |
| --- | --- | :---: | --- |
| `GET` | `/reports/` | 🗂️👑 | The export page. |
| `GET` | `/reports/export/<report_type>` | 🗂️👑 | Builds the Excel file and downloads it. |

`report_type` is one of: `attendance`, `assets`, `visitors`, `programmes`, `labs`, `provinces`.
Anything else errors.

Narrow it with `province_id`, `lab_id`, `start_date`, `end_date`.

Every workbook has two sheets: **Raw Data** and **Summary**.

> **Reports vs the register exports.** `/reports/` is the cross-cutting one — pick a type, get
> the whole network. `/<register>/export` is the "download what I'm looking at" one, with the
> page's filters already applied. Different jobs.

---

## Administration

All 👑 **Admin only**.

| | Route | What happens |
| --- | --- | --- |
| `GET` | `/admin/` | Users, labs and provinces in one console. |
| `POST` | `/admin/users` | Create a user. **Returns a generated temporary password.** **JSON** |
| `POST` | `/admin/users/<user_id>/update` | Change details, role or assigned lab. |
| `POST` | `/admin/users/<user_id>/delete` | Remove them. |
| `POST` | `/admin/users/<user_id>/reset-password` | New temporary password. **JSON** |
| `POST` | `/admin/labs` | Create a lab — **including its geo-fence**. |
| `POST` | `/admin/labs/<lab_id>/update` | Change it. |
| `POST` | `/admin/labs/<lab_id>/delete` | Remove it. |
| `POST` | `/admin/provinces` | Create a province. |
| `POST` | `/admin/provinces/<province_id>/update` | Change it. |
| `POST` | `/admin/provinces/<province_id>/delete` | Remove it. |

**User fields:** `full_name`, `staff_number`, `email`, `role`, `assigned_lab_id`, `active`
**Lab fields:** `name`, `province_id`, `latitude`, `longitude`, `radius_meters`

> `latitude`, `longitude` and `radius_meters` are the geo-fence. Get them wrong and the lab's
> trainees cannot log in at all.

---

## Audit

| | Route | Who | What happens |
| --- | --- | :---: | --- |
| `GET` | `/audit/` | 👑 | Who created, changed or deleted what. Filterable by date. |

---

## Talking JSON

A few routes answer JSON when you ask in JSON. This is how the "Add" modals save without a page
reload — it is not a general-purpose API.

**Ask like this:**

```http
POST /programmes/create
Content-Type: application/json
X-CSRFToken: <token>
```
```json
{
  "title": "Career Expo",
  "date": "2026-06-12",
  "start_time": "09:00",
  "end_time": "12:00",
  "lab_id": "1",
  "facilitators": ["2", "3"]
}
```

> **Multi-value fields come as an array.** `facilitators` is the only one today. It is worth
> knowing that this was a real bug once: the client used to flatten multi-selects and quietly
> send only the last value, so a programme with three facilitators saved with one.

**It worked:**

```json
{
  "success": true,
  "message": "Programme logged successfully.",
  "row_html": "<tr data-id=\"5\" ...>…</tr>",
  "reload": false,
  "reset": true
}
```

| Field | What the client does with it |
| --- | --- |
| `success` | Decides toast colour. |
| `message` | Shown as the toast. |
| `row_html` | A rendered table row, dropped straight into the page. No reload. |
| `reload` | Reload the page instead, if true. |
| `reset` | Clear the form. |
| `redirect` | Navigate here, when present. |
| `temporary_password` | Admin user-create and password-reset only — shown in a modal so it can be copied. |

**It didn't:**

```json
{
  "success": false,
  "message": "Unable to log programme. title: This field is required."
}
```

…with a **400**.

---

## The whole list

53 routes, if you want to scan them at a glance.

<details>
<summary><b>Every route</b></summary>

```
GET       /                                          🌐
GET,POST  /login                                     🌐
GET       /logout                                    🔒
GET,POST  /reset-password                            🔒
GET       /dashboard/                                🔒

GET       /attendance/                               🔒
POST      /attendance/clock-in                       🔒
POST      /attendance/clock-out                      🔒
GET       /attendance/export-timesheet               🔒

GET       /assets/                                   🔸
POST      /assets/create                             🔸  JSON
POST      /assets/<asset_id>/update                  🔸
POST      /assets/<asset_id>/delete                  🔸
GET       /assets/export                             🗂️👑

GET       /visitors/                                 🔸
POST      /visitors/create                           🔸  JSON
POST      /visitors/<visitor_id>/update              🔸
POST      /visitors/<visitor_id>/delete              🔸
GET       /visitors/export                           🗂️👑

GET       /programmes/                               🔸
POST      /programmes/create                         🔸  JSON
POST      /programmes/<programme_id>/update          🔸
POST      /programmes/<programme_id>/delete          🔸
GET       /programmes/export                         🗂️👑

GET       /enquiries/                                🔸
POST      /enquiries/create                          🔧  JSON
POST      /enquiries/<enquiry_id>/edit               🔧
POST      /enquiries/<enquiry_id>/delete             🔧
POST      /enquiries/<enquiry_id>/assign             👑
POST      /enquiries/<enquiry_id>/reassign           👑
POST      /enquiries/<enquiry_id>/start              🗂️👑
POST      /enquiries/<enquiry_id>/resolve            🗂️👑
POST      /enquiries/<enquiry_id>/not-resolved       🗂️👑
POST      /enquiries/<enquiry_id>/close              👑
POST      /enquiries/<enquiry_id>/reopen             👑
GET,POST  /enquiries/track                           🌐

GET       /announcements/manage                      🗂️👑
POST      /announcements/create                      🗂️👑
GET       /announcements/poster/<filename>           🌐

GET       /reports/                                  🗂️👑
GET       /reports/export/<report_type>              🗂️👑

GET       /admin/                                    👑
POST      /admin/users                               👑  JSON
POST      /admin/users/<user_id>/update              👑
POST      /admin/users/<user_id>/delete              👑
POST      /admin/users/<user_id>/reset-password      👑  JSON
POST      /admin/labs                                👑
POST      /admin/labs/<lab_id>/update                👑
POST      /admin/labs/<lab_id>/delete                👑
POST      /admin/provinces                           👑
POST      /admin/provinces/<province_id>/update      👑
POST      /admin/provinces/<province_id>/delete      👑

GET       /audit/                                    👑
```

</details>

---

→ [Permissions matrix](permissions-matrix.md) · [ERD](erd.md) · [README](../README.md)
