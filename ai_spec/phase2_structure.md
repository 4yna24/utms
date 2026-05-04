# Phase 2 Structure Summary

This document explains the current structure after the applicant submission and OIDB review work was added.

## What Changed

The app moved from simple role shell pages to an in-workspace dashboard model.

- The dashboard now behaves like a workspace with button-style tabs.
- Tab clicks switch content inside the dashboard instead of redirecting to other pages.
- Applicant submission is rendered inline inside the dashboard workspace.
- OIDB document review is rendered inline inside the dashboard workspace.
- The unused panel badge was removed because state is now communicated by the workspace content itself.
- The dashboard workspace is now the primary interaction surface for these flows.

## Current Structure

### 1. Configuration

File: `app2/app/config.py`

This file now holds phase and workspace flags used by the dashboard and submission flow:

- `APPLICATION_SUBMISSION_PERIOD_OPEN`
- `APPLICATION_REQUIRED_DOCUMENT_SLOTS`
- `APPLICATION_UPLOAD_SUBDIR`

It still also defines the role list and dashboard tab metadata.

### 2. Data Models

Files:
- `app2/app/models/user.py`
- `app2/app/models/application.py`
- `app2/app/models/__init__.py`

The model structure now looks like this:

- `User`
  - authentication account
  - one optional `Application`
- `Application`
  - owned by one applicant
  - contains the core submission fields
  - has many `ApplicationDocument` rows
- `ApplicationDocument`
  - stores document slot number
  - stores original file name
  - stores saved file path/name
  - supports document slots 1 to 4

### 3. Dashboard Workspace

File: `app2/app/routes/dashboard.py`

The dashboard route now loads role-specific workspace data directly:

- Applicant role gets the current application if one exists.
- OIDB role gets the submitted applications list.
- The template renders all workspace panels in place.

File: `app2/app/templates/dashboard.html`

The dashboard template now has:

- a button-style tab strip
- one main overview panel
- role-specific panels rendered in the same workspace area
- inline applicant form controls
- inline OIDB expandable application list

### 4. Applicant Submission Flow

File: `app2/app/routes/applicant.py`

This route now supports real submission behavior:

- `GET /api/applicant/submit-documents`
  - renders the applicant submission workspace
- `POST /api/applicant/submit-documents`
  - validates required fields
  - checks submission period state
  - creates the application
  - saves optional PDF files in slots 1 to 4

File: `app2/app/templates/applicant_submit.html`

This template provides the standalone applicant submission screen for direct access, while the same form logic is also rendered inline inside the dashboard workspace.

### 5. OIDB Review Flow

File: `app2/app/routes/oidb.py`

This route now loads submitted applications with applicant and document data.

File: `app2/app/templates/oidb_check_documents.html`

This template renders a read-only expandable list of applications for review, and the same review content is also shown inline inside the dashboard workspace.

### 6. Dashboard Tab Strategy

The dashboard uses button-style tabs rather than classic browser tabs.

- The top strip acts as a workspace selector.
- The main panel shows summary cards and jump buttons.
- Each selected tab swaps the visible panel inside the same page.
- No panel badge is shown because open/closed state is not the primary signal anymore.

## Folder Responsibility Changes

### `app/routes/`

Routes remain thin and are responsible for:

- request handling
- access control
- loading model data
- passing data to templates

### `app/models/`

Models now carry the actual submission data structure.

### `app/templates/`

Templates now contain the workspace UI and the in-page tab/panel behavior.

### `ai_spec/`

The Phase 2 docs now document the submission workflow, the dashboard workspace structure, and the current phase roadmap.

## Resulting User Experience

- Applicants stay inside the dashboard workspace while switching sections.
- The submit flow supports creating an application with required fields.
- Documents are optional for now, but PDF uploads are supported.
- OIDB can inspect submitted applications without leaving the workspace.

## Notes

This phase intentionally does not include:

- applicant edit and resubmit workflow
- OIDB approve/return actions
- document error marking
- redirecting submissions to later approval stages

Those can be added in a later phase without changing the current structure.
