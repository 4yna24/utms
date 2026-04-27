# Phase 2 - Applicant Submission and OIDB Document Check

## 1. Scope
This phase introduces a working flow for applicant-side application submission and OIDB-side read-only document checking.

## 2. Applicant Submission Period
- Add a configuration flag to control application submission period availability.
- For now, keep this flag active (`True`).
- Applicant submission screen must honor this flag and show period state.

## 3. Application Ownership and Constraints
- One applicant can own at most one application.
- If no application is tied to the logged-in applicant:
  - Applicant can create a new application from the submit screen.
  - Required form fields must be validated server-side.
- If an application already exists:
  - Submit screen must show a message that the applicant already has an application.
  - Show existing application details in read-only mode.
  - Future edit/resubmit action can be added later (not in this phase).

## 4. Application and Document Data Model
- Add `Application` entity/model tied to applicant (`User`) with one-to-many relation to `Document`.
- Add `Document` entity/model storing:
  - document slot number (`1..4`)
  - original document name
  - stored file path/name
  - PDF-only file type enforcement
- Application may be created without any document for now.
- Document slots are fixed for this phase:
  - Document #1
  - Document #2
  - Document #3
  - Document #4

## 5. Applicant Submit Screen Behavior
- Route remains role-restricted to applicant users.
- GET:
  - Render submission form when no application exists.
  - Render already-submitted message when application exists.
- POST:
  - Validate required fields.
  - Validate files as PDFs if provided.
  - Persist application and optional documents.
  - Show success feedback and redirect back to submit screen.

## 6. OIDB Check Documents Screen Behavior
- OIDB `check documents` tab should show list of submitted applications.
- Each application item should be expandable to show:
  - basic application information
  - applicant identity info
  - attached document list
- This phase is read-only for OIDB.
- Future actions (out of scope now):
  - mark part of application as error and return to applicant
  - approve and redirect application to next role

## 7. Engineering Rules for This Phase
- Keep route functions thin (validation and orchestration only).
- Use model/class helpers for repeated logic where useful.
- Keep implementation simple (YAGNI): no approval workflow yet.
- Do not break existing role-based dashboard tabs and auth behavior.
