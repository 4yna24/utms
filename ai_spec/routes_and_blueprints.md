# Flask Routing & Blueprint Structure

## Rule
Routes must not contain heavy business logic. They should extract request data, load the needed model data, and return the response or template.

## Blueprint Definitions
1.  **Auth Blueprint (`/auth`):** Handles login, register, e-Devlet integration, and password resets.
2.  **Dashboard Blueprint (`/dashboard`):** A common route that determines the user's role, loads workspace data, and renders the in-page tab workspace.
3.  **API/Action Blueprints (Role Restricted):**
    * `/api/applicant`: Handle document submissions and status checks.
    * `/api/oidb`: Handle waitlist generation and document verification.
    * `/api/dean`: Handle department forwarding actions.
    * `/api/ygk`: Handle Intibak table creation and editing.
    * `/api/ydyo`: Handle English proficiency status updates.

## Current Workspace Behavior
* Dashboard tabs are button-style workspace selectors, not page redirects.
* The dashboard template renders the main overview and role panels in one workspace area.
* Applicant submission and OIDB review are currently visible inside the dashboard workspace.
* Standalone role pages still exist for compatibility, but the dashboard is the primary interaction surface.