# OPELSS Documentation

Documentation for **OPELSS** — the OAU E-Learning Lab Support System.

This folder holds all project documentation: the business case for stakeholders,
technical references for developers, and the training manuals distributed to users.

## Contents

| Document | Audience | Description |
| --- | --- | --- |
| [Business Case](business-case/) | Stakeholders, management | Strategic alignment, scope, finance, risks, and the delivery schedule. |
| [API Documentation](api-documentation.md) | Developers | Every route/endpoint, the roles allowed to call it, parameters, and responses. |
| [ERD](erd.md) | Developers | Entity relationship diagram of the database schema. |
| [Permissions Matrix](permissions-matrix.md) | Developers, management | What each system role (Admin, HQ Trainee, Lab Trainee, public) may do. |
| [Training Manuals](manuals/) | End users | Step-by-step guides, one per role. |

## Training manuals

| Manual | For |
| --- | --- |
| [Administrator Manual](manuals/OPELSS_Administrator_Manual.docx) | Admins — user/lab administration, announcements, full system access. |
| [HQ Trainee Manual](manuals/OPELSS_HQ_Trainee_Manual.docx) | HQ Trainees — cross-lab oversight, enquiry management, reporting. |
| [Lab Trainee Manual](manuals/OPELSS_Lab_Trainee_Manual.docx) | Lab Trainees — clock in/out, assets, visitors, programmes, enquiries. |

## Document formats

- **`.docx`** — the business case and training manuals, which need formal sign-off
  and are distributed to stakeholders and users.
- **`.md`** — technical references, so they render directly on GitHub and diff
  cleanly in pull requests.

## Related

The project [README](../README.md) covers setup, running the app locally, and deployment.
