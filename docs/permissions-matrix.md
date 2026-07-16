# OPELSS Permissions Matrix

What each system role is allowed to do. Derived from the actual authorisation checks in the
code — the `role_required(...)` decorators in `app/utils.py` and the in-view role checks — so
this reflects enforced behaviour, not intent.

---

## Roles

| Role | Data scope | Purpose |
| --- | --- | --- |
| **Lab Trainee** | Their assigned lab only | Runs the day-to-day operations of one lab. |
| **HQ Trainee** | All labs, all provinces | Oversees and supports labs from HQ; handles enquiries and reporting. |
| **Admin** | Everything | Full control, including user and lab administration. |
| **Public** | Public pages only | Students and visitors — no account required. |

**Scoping.** A Lab Trainee is limited to records whose `lab_id` matches their
`assigned_lab_id`. Admin and HQ Trainee see all labs. Attempting to reach another lab's record
returns **403 Forbidden**.

### Legend

| Symbol | Meaning |
| --- | --- |
| ✅ | Allowed. |
| 🔸 | Allowed, restricted to their own lab. |
| ⚠️ | Allowed with a condition (noted below the table). |
| — | Not allowed (403). |

---

## Matrix

### Authentication

| Action | Lab Trainee | HQ Trainee | Admin | Public |
| --- | :---: | :---: | :---: | :---: |
| View landing page | ✅ | ✅ | ✅ | ✅ |
| Log in | ✅ | ✅ | ✅ | ✅ |
| Log out | ✅ | ✅ | ✅ | — |
| Change own password | ✅ | ✅ | ✅ | — |

### Dashboard

| Action | Lab Trainee | HQ Trainee | Admin | Public |
| --- | :---: | :---: | :---: | :---: |
| View dashboard | 🔸 own lab | ✅ all labs | ✅ all labs | — |

### Attendance

| Action | Lab Trainee | HQ Trainee | Admin | Public |
| --- | :---: | :---: | :---: | :---: |
| View attendance page | ✅ | ⚠️ | ⚠️ | — |
| Clock in | ⚠️ | ⚠️ | ⚠️ | — |
| Clock out | ⚠️ | ⚠️ | ⚠️ | — |
| Export own timesheet (PDF) | ✅ | ⚠️ | ⚠️ | — |

> ⚠️ **The attendance routes carry no role check** — they are guarded by `login_required` only.
> What gates them in practice is having an `assigned_lab`: a user without one cannot clock in
> or out. Because the seeded Admin account *is* given an assigned lab, an Admin can clock in.
> These routes are intended for Lab Trainees; the restriction is incidental rather than
> enforced by role.

Clock-in is additionally rejected when the device is outside the lab's configured
`radius_meters`. Clock-out requires a reason when leaving before the scheduled end.

### Assets

| Action | Lab Trainee | HQ Trainee | Admin | Public |
| --- | :---: | :---: | :---: | :---: |
| View asset register | 🔸 own lab | ✅ all | ✅ all | — |
| Add asset | 🔸 own lab | ✅ | ✅ | — |
| Edit asset | 🔸 own lab | ✅ | ✅ | — |
| Delete asset | 🔸 own lab | ✅ | ✅ | — |
| Export to Excel | — | ✅ | ✅ | — |
| Filter by lab / province | — | ✅ | ✅ | — |

### Visitors

| Action | Lab Trainee | HQ Trainee | Admin | Public |
| --- | :---: | :---: | :---: | :---: |
| View visitor log | 🔸 own lab | ✅ all | ✅ all | — |
| Log visitor | 🔸 own lab | ✅ | ✅ | — |
| Edit visitor | 🔸 own lab | ✅ | ✅ | — |
| Delete visitor | 🔸 own lab | ✅ | ✅ | — |
| Export to Excel | — | ✅ | ✅ | — |
| Filter by lab / province | — | ✅ | ✅ | — |

### Programmes

| Action | Lab Trainee | HQ Trainee | Admin | Public |
| --- | :---: | :---: | :---: | :---: |
| View programme register | 🔸 own lab | ✅ all | ✅ all | — |
| Log programme | 🔸 own lab | ✅ | ✅ | — |
| Edit programme (incl. facilitators) | 🔸 own lab | ✅ | ✅ | — |
| Delete programme | 🔸 own lab | ✅ | ✅ | — |
| Assign facilitators | 🔸 own lab | ✅ | ✅ | — |
| Filter by date / facilitator | ✅ | ✅ | ✅ | — |
| Filter by lab / province | — | ✅ | ✅ | — |
| Export to Excel | — | ✅ | ✅ | — |

Any active user may be named as a facilitator, regardless of role.

### Enquiries

| Action | Lab Trainee | HQ Trainee | Admin | Public |
| --- | :---: | :---: | :---: | :---: |
| View enquiry list | 🔸 own lab | ✅ all | ✅ all | — |
| Raise / escalate enquiry | ✅ | — | — | — |
| Edit enquiry | ⚠️ 🔸 | — | — | — |
| Delete enquiry | ⚠️ 🔸 | — | — | — |
| Assign to a handler | — | — | ✅ | — |
| Reassign | — | — | ✅ | — |
| Mark in progress | — | ⚠️ | ✅ | — |
| Mark resolved | — | ⚠️ | ✅ | — |
| Mark not resolved | — | ⚠️ | ✅ | — |
| Close | — | — | ✅ | — |
| Reopen | — | — | ✅ | — |
| Track by reference number | — | — | — | ✅ |

> ⚠️ **Lab Trainee edit/delete** — permitted only while the enquiry status is still `Open`.
> Once assigned it can no longer be edited or deleted by the lab.
>
> ⚠️ **HQ Trainee start/resolve/not-resolved** — permitted only for enquiries **assigned to
> them**. An Admin may act on any enquiry.

Only **Lab Trainees** can raise enquiries; only **Admins** can assign, reassign, close or
reopen them.

### Announcements

| Action | Lab Trainee | HQ Trainee | Admin | Public |
| --- | :---: | :---: | :---: | :---: |
| View announcements (landing page) | ✅ | ✅ | ✅ | ✅ |
| Manage announcements | — | ✅ | ✅ | — |
| Create announcement | — | ✅ | ✅ | — |
| View poster image | ✅ | ✅ | ✅ | ✅ |

> Announcement management is **Admin and HQ Trainee** (`role_required("Admin", "HQ Trainee")`).

### Reports

| Action | Lab Trainee | HQ Trainee | Admin | Public |
| --- | :---: | :---: | :---: | :---: |
| View reports page | — | ✅ | ✅ | — |
| Export any report type | — | ✅ | ✅ | — |

Report types: attendance, assets, visitors, programmes, labs, provinces.

### Administration

| Action | Lab Trainee | HQ Trainee | Admin | Public |
| --- | :---: | :---: | :---: | :---: |
| View admin dashboard | — | — | ✅ | — |
| Create / edit / delete user | — | — | ✅ | — |
| Reset a user's password | — | — | ✅ | — |
| Assign roles | — | — | ✅ | — |
| Create / edit / delete lab | — | — | ✅ | — |
| Set lab geo-coordinates and radius | — | — | ✅ | — |
| Create / edit / delete province | — | — | ✅ | — |

### Audit log

| Action | Lab Trainee | HQ Trainee | Admin | Public |
| --- | :---: | :---: | :---: | :---: |
| View audit log | — | — | ✅ | — |

---

## Summary by role

### Lab Trainee
Runs one lab. Clocks in/out from within the lab's geo-fence, maintains that lab's assets,
visitors and programmes, and raises enquiries to HQ. Sees only their own lab's data, and
cannot export to Excel or reach the reports, admin or audit sections.

### HQ Trainee
Oversees all labs. Sees every lab's assets, visitors, programmes and enquiries; filters by
lab and province; exports to Excel and generates reports; manages announcements; and handles
the enquiries assigned to them. Cannot administer users or labs, cannot assign or close
enquiries, and cannot view the audit log.

### Admin
Full access, including everything an HQ Trainee can do, plus user/lab/province administration,
password resets, the full enquiry workflow (assign, reassign, close, reopen) and the audit log.

### Public (no login)
Views the landing page, current announcements and poster images, and tracks an enquiry by its
reference number. No other access.

---

## How it is enforced

**Decorator.** `role_required(*roles)` in `app/utils.py` aborts with **403** when
`current_user.role` is not in the allowed set. Used by the admin, audit and announcements
blueprints.

```python
@admin_bp.route("/users", methods=["POST"])
@login_required
@role_required("Admin")
def add_user():
    ...
```

**In-view checks.** The operational modules check the role inside the view, because the rule
depends on the record — a Lab Trainee is allowed in, but only for their own lab:

```python
if current_user.role == "Lab Trainee" and programme.lab_id != current_user.assigned_lab_id:
    abort(403)
```

**Two layers.** Role determines whether the module is reachable at all; `assigned_lab_id`
determines which records within it are reachable.

---

## Notes for reviewers

Two behaviours here are worth a decision rather than being assumed correct:

1. **Attendance has no role check.** Any authenticated user with an assigned lab can clock in
   and out, including an Admin. If clocking in should be Lab-Trainee-only, that needs an
   explicit guard.
2. **Enquiry edit/delete is Lab-Trainee-only.** Admins and HQ Trainees cannot edit or delete an
   enquiry at all — they can only move it through the workflow. This may well be deliberate
   (the lab owns the record it raised), but it is unusual enough to call out.

---

## Related documentation

- [API documentation](api-documentation.md) — the routes these permissions apply to.
- [ERD](erd.md) — where `role` and `assigned_lab_id` live.
- [Project README](../README.md)
