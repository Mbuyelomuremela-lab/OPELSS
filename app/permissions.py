"""Central role/permission map for OPELSS.

This module is the single source of truth for "which role can see/use which
part of the system". Both the sidebar (what tabs render) and the route guards
(what URLs are reachable) read from the same map here, so the menu and the
actual permissions can never drift apart.

Job-function roles live in the HQ. The "Lab Trainee" role is intentionally
left exactly as it always behaved — its tabs are preserved unchanged.
"""

from flask import request, abort
from flask_login import current_user

# --- Modules (one per feature area / tab) --------------------------------
DASHBOARD = "dashboard"
ATTENDANCE = "attendance"
VISITORS = "visitors"
ENQUIRIES = "enquiries"
PROGRAMMES = "programmes"
ASSETS = "assets"
ANNOUNCEMENTS = "announcements"
REPORTS = "reports"
AUDIT = "audit"
ADMIN = "admin"  # the Admin/Developer console (labs, provinces, user management)

# --- Roles ---------------------------------------------------------------
LAB_TRAINEE = "Lab Trainee"

# HQ job-function roles, ordered from least to most access.
HQ_ROLES = [
    "Trainee student support",
    "Senior student support",
    "Trainee multimedia",
    "Senior multimedia",
    "Trainee resource manager",
    "Senior resource manager",
    "Manager",
    "Developers",
]

ALL_ROLES = HQ_ROLES + [LAB_TRAINEE]

# The "everything" roles — these inherit what used to be the single "Admin"
# role's elevated privileges (e.g. assigning/closing enquiries, exports,
# reports, audit). "Developers" additionally own the Admin console.
ELEVATED_ROLES = {"Senior resource manager", "Manager", "Developers"}

# --- The map: role -> set of modules it can access -----------------------
ROLE_TABS = {
    "Trainee student support": {DASHBOARD, VISITORS, ENQUIRIES, PROGRAMMES},
    "Senior student support": {DASHBOARD, VISITORS, ENQUIRIES, PROGRAMMES, ANNOUNCEMENTS},
    "Trainee multimedia": {DASHBOARD, PROGRAMMES, ANNOUNCEMENTS},
    "Senior multimedia": {DASHBOARD, PROGRAMMES, ANNOUNCEMENTS},
    "Trainee resource manager": {DASHBOARD, PROGRAMMES, ASSETS},
    "Senior resource manager": {
        DASHBOARD, VISITORS, ENQUIRIES, PROGRAMMES, ASSETS, ANNOUNCEMENTS, REPORTS, AUDIT,
    },
    "Manager": {
        DASHBOARD, VISITORS, ENQUIRIES, PROGRAMMES, ASSETS, ANNOUNCEMENTS, REPORTS, AUDIT,
    },
    "Developers": {
        DASHBOARD, VISITORS, ENQUIRIES, PROGRAMMES, ASSETS, ANNOUNCEMENTS, REPORTS, AUDIT, ADMIN,
    },
    # Preserved verbatim — do not change without touching the Lab Trainee flow.
    LAB_TRAINEE: {DASHBOARD, ATTENDANCE, ASSETS, VISITORS, ENQUIRIES, PROGRAMMES},
}

# Which blueprint maps to which module, for the central route guard.
# Blueprints not listed here (auth, dashboard, attendance, static) are handled
# by their own decorators or are always available to authenticated users.
BLUEPRINT_MODULE = {
    "visitors": VISITORS,
    "enquiries": ENQUIRIES,
    "programmes": PROGRAMMES,
    "assets": ASSETS,
    "announcements": ANNOUNCEMENTS,
    "reports": REPORTS,
    "audit": AUDIT,
    "admin": ADMIN,
}

# Form dropdown choices (kept in role order, HQ first then Lab Trainee).
ROLE_CHOICES = [(r, r) for r in ALL_ROLES]


def can_access(role, module):
    """True if the given role is allowed to use the given module."""
    return module in ROLE_TABS.get(role, set())


def visible_tabs(role):
    """Set of modules a role can see — used to render the sidebar."""
    return ROLE_TABS.get(role, set())


def is_elevated(role):
    """True for the 'everything' roles that hold old 'Admin' privileges."""
    return role in ELEVATED_ROLES


# Who can run the enquiry desk (assign / close / reopen / reassign, and act on
# any enquiry, not just their own): the elevated roles plus the student-support
# lead who actually manages enquiries day to day.
ENQUIRY_MANAGER_ROLES = ELEVATED_ROLES | {"Senior student support"}


def can_manage_enquiries(role):
    """True for roles allowed to assign/close/reassign enquiries."""
    return role in ENQUIRY_MANAGER_ROLES


def roles_with_module(module):
    """All roles whose map includes `module` (e.g. assignable enquiry staff)."""
    return [role for role, mods in ROLE_TABS.items() if module in mods]


def register_access_guard(app):
    """Install a single before-request guard enforcing module access.

    A hidden tab is not enough on its own — its URL must be blocked too. This
    guard makes the same map that hides the tab also reject the route, so there
    are no "hidden but reachable" pages.
    """

    @app.before_request
    def _enforce_module_access():
        # Let @login_required handle unauthenticated users (redirect to login).
        if not getattr(current_user, "is_authenticated", False):
            return None
        module = BLUEPRINT_MODULE.get(request.blueprint)
        if module and not can_access(current_user.role, module):
            abort(403)
        return None
