# Flask Routing & Blueprint Structure

## Rule
Routes must not contain heavy business logic. They should extract request data, call the appropriate methods from `/app/classes/`, and return the response or template.

## Blueprint Definitions
1.  **Auth Blueprint (`/auth`):** Handles login, register, e-Devlet integration, and password resets.
2.  **Dashboard Blueprint (`/dashboard`):** * A common route that determines the user's role and renders the appropriate template with the correct tabs.
3.  **API/Action Blueprints (Role Restricted):**
    * `/api/applicant`: Handle document submissions and status checks.
    * `/api/oidb`: Handle waitlist generation and document verification.
    * `/api/dean`: Handle department forwarding actions.
    * `/api/ygk`: Handle Intibak table creation and editing.
    * `/api/ydyo`: Handle English proficiency status updates.