# Use Case Difference: Original Prototype vs. Current Implementation

> Compares the original prototype use cases (`srs/original usecases/UTS_Use_Cases(1).md`) against what the system actually does today (2026-05-30).

---

## 1. UC-1 — Register to System

| Aspect | Original Prototype | Current Implementation |
|---|---|---|
| Required fields | Email, password, TC number, full name, phone number | Email, password, password confirmation only |
| Email confirmation | Step 3–4: system sends confirmation link; applicant clicks it | **Not present.** Account is created immediately on submit. |
| TC number validation | 11 digits, must end with even digit | Not collected. |
| Full name at registration | Required field | Not collected at registration. |
| Phone number | Required field | Not collected. |
| Password rules | Min 8, max 32 chars; English letters, digits, underscores only | Non-empty check only — no length or character constraints enforced. |
| Timeout on confirmation link | Mentioned in alternative course | Not applicable; no email flow exists. |

**Verdict:** Substantially simplified. Core registration works, but identity fields (TC, name, phone) and email verification are absent.

---

## 2. UC-2 — Log In

| Aspect | Original Prototype | Current Implementation |
|---|---|---|
| Actor | Applicant | Applicant — separate endpoint from staff |
| Core flow | Email + password → home page | Email + password → dashboard. Works. |
| Activation period gate | Exception: login blocked outside activation period | Not enforced at the login route. |
| Forgot password link | Alternative course → UC-3 | Password reset UI does not exist. |
| Concurrent session prevention | Stated as special requirement | Not explicitly enforced. |

**Verdict:** Core login is implemented. Activation period gate and concurrent session enforcement are not.

---

## 3. UC-3 — Reset the Password

| Aspect | Original Prototype | Current Implementation |
|---|---|---|
| Email-based reset flow | Full flow: submit email → receive link → click link → enter new password | `request_password_reset` and `reset_password` methods exist in `AuthClass` as Phase 1 placeholders. No email is sent. No UI route exposes this. |
| E-Devlet alternative | Applicant can authenticate via E-Devlet to skip to password entry | Not implemented. |
| Token expiry | Implied by the flow | Not applicable; no token is issued. |
| "Account locked" after failed attempts | Exception 2.EX.1 | Not implemented. |

**Verdict:** Password reset is non-functional. Service layer stubs exist but are not wired to any UI or email service.

---

## 4. UC-4 — Submit the Documents

| Aspect | Original Prototype | Current Implementation |
|---|---|---|
| Core flow | Upload documents; system validates format and size | Implemented. Documents are uploaded in defined slots with format enforcement. |
| Required documents listed | Criminal record, English proficiency proof, transcript, course curriculum | **Different.** Current required slots are: Student Certificate, Transcript, YKS Score Report. English Proficiency Certificate is optional (slot 4). Criminal record and course curriculum are not required. |
| Automated script verification | "verified by an automated script" mentioned in description | **Not implemented.** No automated content or validity check of uploaded files occurs. |
| Extension format check | Step 2: system checks extension | Implemented (PDF enforced). |
| File size check | Step 3: system checks file size | Implemented. |
| Activation period assumption | System activated in a particular time period | Controlled by `APPLICATION_SUBMISSION_PERIOD_OPEN` flag. Works. |
| Form fields | Not specified beyond documents | Current system collects: full name, ID number, source university, target program, semester, GPA, enrollment status. |

**Verdict:** Core upload is implemented. Document set has changed significantly. Automated script verification is absent.

---

## 5. UC-5 — Track Result

| Aspect | Original Prototype | Current Implementation |
|---|---|---|
| Core flow | Applicant presses track button → sees status | Implemented via "Track Application" dashboard tab. |
| Real-time tracking | Described as "realtime" | Tab is fetched via AJAX on tab click; not a live-push feed. |
| Error: application not found | Exception 2.EX.1a | Shown as "No application found." message on the panel. |
| Status detail | Not specified | Shows a named step-tracker with 6 pipeline stages. Not all statuses map to tracker steps yet (e.g., `forwarded_to_ygk`, `approved` are unmapped). |

**Verdict:** Largely implemented. Step-tracker visualisation is an improvement over the original spec. Real-time push is not present.

---

## 6. UC-6 — Resubmit Application

| Aspect | Original Prototype | Current Implementation |
|---|---|---|
| Trigger | Applicant views rejection reason and resubmits | Implemented: applicant sees `oidb_notes` on the form and can resubmit when status is `returned`. |
| Per-document update | Applicant clicks "Update" next to a specific document | Current form re-uploads all document slots (any slot can be replaced). Per-document individual buttons not present. |
| Deadline enforcement | "Deadline for documents didn't expire yet" as precondition | Controlled by `APPLICATION_RESUBMISSION_ALLOWED` flag, not a date-based deadline. |
| Unsupported format exception | 5.EX.1 | Enforced — unsupported formats are rejected. |
| Network failure exception | 6.EX.2 | Not specifically handled; generic server error. |

**Verdict:** Core resubmission is implemented. Per-document granular updating is not present.

---

## 7. UC-21 — Applicant Cancels the Application

| Aspect | Original Prototype | Current Implementation |
|---|---|---|
| Core flow | Applicant lists active applications → selects one → cancels | Implemented. Single application per account; cancel button is on the submit/track panel. |
| Confirmation pop-up | Steps 5–6: confirmation dialog before cancel | Not present. Cancel is a single POST — no JS confirmation dialog. |
| Status scope | "Enrollment time interval has yet to start" | Controlled by `APPLICATION_CANCELLATION_ALLOWED` flag. Status must be `submitted` or `returned`. |
| Permanence | Assumed permanent | Permanent — no undo UI. |
| Post-cancel state label | "Cancelled applications" list | Status is set to `cancelled`; tracked on the dashboard. |

**Verdict:** Core cancellation is implemented. Confirmation dialog is absent.

---

## 8. UC-33 — Log In with E-Devlet

| Aspect | Original Prototype | Current Implementation |
|---|---|---|
| E-Devlet button | Applicant presses "Login via E-Devlet" | Button/route does not exist in the UI. |
| OAuth/authorization flow | System redirects to E-Devlet, gets token | `login_with_edevlet` method always returns "e-Devlet integration not yet implemented." |
| Error handling | Error from E-Devlet service or time-period closed | Not applicable. |

**Verdict:** Not implemented. Stub method exists only.

---

## 9. UC-7 — Dean Receive the Documents

| Aspect | Original Prototype | Current Implementation |
|---|---|---|
| Trigger | Admission period has ended; Dean lists applications | Implemented as "Receive & Forward Applications" tab. No hard period-end gate — shows applications in `forwarded_to_dean` status at any time. |
| Scope | Dean receives applications for their faculty | Applications reaching Dean have already passed OIDB and YDYO. Dean sees all `forwarded_to_dean` applications. |

**Verdict:** Implemented with a simpler trigger (status-based rather than period-based).

---

## 10. UC-8 — Dean Forward the Document

| Aspect | Original Prototype | Current Implementation |
|---|---|---|
| Automatic forwarding | Step 1: Dean presses "automatically forward" button | Partially: forward-all exists but is **not implemented** ("not yet implemented" error). |
| Manual forwarding | Alternative course for system error | Manual per-application forwarding to YGK **is** implemented (with faculty selection). |
| Error handling | System is not working | Generic database error handling. |

**Verdict:** Manual forwarding is implemented. Automatic bulk forwarding is not.

---

## 11. UC-18 — YGK Create Intibak Tables

| Aspect | Original Prototype | Current Implementation |
|---|---|---|
| Applicant selection | YGK picks from pending list | Route to view `forwarded_to_ygk` applications exists. Selection to begin intibak is not implemented. |
| System-generated matches | ECTS-based matching script | **Not implemented.** |
| Manual adjustment UI | Side-by-side transcript vs. IZTECH curriculum view | **Not implemented.** |
| Save and submit table | Step 3 | **Not implemented.** |
| All special requirements | Course equivalence validation, audit log, side-by-side view | **None implemented.** |

**Verdict:** Entirely empty. YGK can see a list of forwarded applications and approve them, but the intibak workflow does not exist.

---

## 12. UC-19 — ÖİDB Retrieve the Documents

| Aspect | Original Prototype | Current Implementation |
|---|---|---|
| Core flow | OIDB lists applications and related documents | Implemented as "Check Documents" tab. |
| Student Affairs forwarding prerequisite | Applications forwarded by Student Affairs first | No "Student Affairs" role exists. Applications go directly to OIDB after submission. |
| Permission by database manager | Exception: DB admin may not have granted access | Role-based access is enforced by `@role_required("oidb")` decorator. No per-user DB-level permission. |

**Verdict:** Implemented with a simplified workflow (no Student Affairs intermediary).

---

## 13. UC-20 — Create and Announce Asil/Yedek Tables

| Aspect | Original Prototype | Current Implementation |
|---|---|---|
| Score formula | (x/y*100*0.9) + (z*0.1) | **Not implemented.** No scoring logic exists anywhere in the codebase. |
| DGS/foreign national handling | Special base-year score rule | **Not implemented.** |
| Ranking and quota selection | Top N from ranked list | **Not implemented.** |
| Public announcement | Table uploaded publicly | **Not implemented.** The "Create Waitlist Table" tab returns a Phase 1 JSON shell. |

**Verdict:** Entirely empty.

---

## 14. UC-27 — OIDB Check Documents

| Aspect | Original Prototype | Current Implementation |
|---|---|---|
| Eye icon to open details | Step 1: press Eye icon | Implemented via expand row button in the dashboard table. |
| Make changes | Step 4: OIDB edits application details | OIDB can return the application with notes. Direct field editing by OIDB is not present. |
| Save changes | Step 5 | Return-with-notes is saved. No generic field-editing form. |

**Verdict:** Core document review is implemented. Free-form field editing by OIDB is not.

---

## 15. UC-29 and UC-30 — YDYO Receive and Process Applications

| Aspect | Original Prototype | Current Implementation |
|---|---|---|
| Receive list | UC-29: YDYO lists applications | Implemented as "Set Prep School Status" tab. |
| Mark status | UC-30: dropdown to set status, save and forward | Implemented. Dropdown sets `prep_school_status` and forwards to `forwarded_to_dean`. |
| Connection error | Exception 4.EX.1 | Generic database error handled. |

**Verdict:** Both UC-29 and UC-30 are implemented.

---

## 16. UC-32 — Staff Login

| Aspect | Original Prototype | Current Implementation |
|---|---|---|
| Single staff login | Original covered Dean only | Current system has a unified `/auth/staff/login` with a role dropdown for oidb, dean, ygk, ydyo. |
| Admin login | Not mentioned | Implemented at `/auth/admin/login` (separate, not publicly linked). |

**Verdict:** Expanded and implemented.

---

## Use Cases Present in Current System but Absent from Original

| UC | Description |
|---|---|
| UC-16 (current) | OIDB cancel forward-to-YDYO (revert forwarded application back to submitted) |
| UC-14 (current) | OIDB return application to applicant with notes |
| UC-26 (current) | Admin: change user roles |
| UC-27 (current) | Admin: view feature flag configuration |
| UC-28 (current) | Admin: create database backup |
| UC-29 (current) | Admin: restore database from backup |

---

## Summary Table

| Original UC | Title | Status in Current System |
|---|---|---|
| UC-1 | Register | Implemented — simplified (no TC/phone/name, no email confirmation) |
| UC-2 | Log In (Applicant) | Implemented — activation period gate not enforced |
| UC-3 | Reset Password | Not functional — stub only, no email service |
| UC-4 | Submit Documents | Implemented — different document set; no automated content check |
| UC-5 | Track Result | Implemented — step tracker UI added |
| UC-6 | Resubmit Application | Implemented — no per-document granularity |
| UC-21 | Cancel Application | Implemented — no confirmation dialog |
| UC-33 | Login via E-Devlet | Not implemented |
| UC-7 | Dean Receive Documents | Implemented — no period gate |
| UC-8 | Dean Forward Documents | Single forward implemented; bulk not implemented |
| UC-18 | YGK Create Intibak Tables | Not implemented — Phase 1 placeholder |
| UC-19 | OIDB Retrieve Documents | Implemented — no Student Affairs role |
| UC-20 | Create Asil/Yedek Tables | Not implemented — Phase 1 placeholder |
| UC-27 | OIDB Check Documents | Implemented — no free-form field editing |
| UC-29 | YDYO Receive Application List | Implemented |
| UC-30 | YDYO Mark and Forward | Implemented |
| UC-32 | Staff Login | Implemented — unified multi-role login |
