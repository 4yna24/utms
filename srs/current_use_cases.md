# UTMS System — Current Use Cases

> Status as of 2026-05-30. Use cases reflect only what is actually implemented in the codebase.
> Cases marked **EMPTY** have a named route or tab but no real logic behind it.

---

## Actors

| Actor | Description |
|---|---|
| Applicant | A student applying for horizontal transfer, self-registered |
| OIDB Staff | Student affairs office staff; first staff stop after submission |
| YDYO Staff | Foreign language school staff; marks English prep requirement |
| Dean | Dean's office; routes applications to YGK |
| YGK | Transfer committee; reviews and approves/rejects |
| Admin | System administrator; manages users and database |

---

## 1. Authentication Use Cases

### UC-1: Applicant Register

**Actor:** Applicant
**Priority:** High | **Frequency:** Once per applicant

**Preconditions:**
- PRE-1. Applicant is not already logged in.
- PRE-2. Applicant has a valid email address.

**Postconditions:**
- POST-1. A new applicant account is created.
- POST-2. Applicant is taken to the login page.

**Normal Course of Events:**
1. Applicant opens the applicant registration page.
2. Applicant enters email address, password, and password confirmation.
3. Applicant presses "Register as Applicant".
4. Applicant sees a success message and is taken to the login page.

**Alternative Courses:**
- 3.AC.1. Email or password field is empty → Applicant sees "Email and password are required." and stays on the form.
- 3.AC.2. Passwords do not match → Applicant sees "Passwords do not match." and stays on the form.
- 3.AC.3. Email is already registered as an applicant → Applicant sees a duplicate account error and stays on the form.

**Exceptions:**
- 3.EX.1. Unexpected server error → Applicant sees a generic error message.

**Special Requirements:**
- Password is stored hashed.
- Email is normalised to lowercase.

**Not Implemented:**
- Email confirmation link is not sent. Registration is immediate with no verification step.
- TC identity number, full name, and phone number are not collected at registration.

---

### UC-2: Applicant Login

**Actor:** Applicant
**Priority:** High | **Frequency:** Multiple times per applicant per year

**Preconditions:**
- PRE-1. Applicant is not already logged in.
- PRE-2. Applicant has a registered account.

**Postconditions:**
- POST-1. Applicant is taken to their personal dashboard.

**Normal Course of Events:**
1. Applicant opens the applicant login page.
2. Applicant enters email and password.
3. Applicant presses "Login as Applicant".
4. Applicant sees their personal dashboard.

**Alternative Courses:**
- 3.AC.1. Email or password is empty → Applicant sees "Email and password are required." and stays on the login page.
- 3.AC.2. Email or password is incorrect → Applicant sees "Invalid email or password." and stays on the login page.

**Exceptions:**
- 3.EX.1. Unexpected server error → Applicant sees a database error message.

**Special Requirements:**
- If already logged in, visiting the login page redirects immediately to the dashboard.

---

### UC-3: Staff Login

**Actor:** OIDB Staff, YDYO Staff, Dean, YGK
**Priority:** High | **Frequency:** Multiple times per year

**Preconditions:**
- PRE-1. User is not already logged in.
- PRE-2. User has a registered account with the matching staff role.

**Postconditions:**
- POST-1. User is taken to their role-specific dashboard.

**Normal Course of Events:**
1. User opens the staff login page.
2. User selects their role from the dropdown.
3. User enters email and password.
4. User presses "Login to Staff Workspace".
5. User sees their role-specific dashboard.

**Alternative Courses:**
- 2.AC.1. An invalid role is selected → User sees "Invalid role selected." and stays on the login page.
- 4.AC.1. Email or password is incorrect → User sees "Invalid email or password." and stays on the login page.

**Exceptions:**
- 4.EX.1. Unexpected server error → User sees a database error message.

---

### UC-4: Admin Login

**Actor:** Admin
**Priority:** High | **Frequency:** As needed

**Preconditions:**
- PRE-1. Admin account exists (created via CLI; not self-registerable).
- PRE-2. Admin navigates directly to the admin login page (not linked from the public portal).

**Postconditions:**
- POST-1. Admin is taken to the admin dashboard.

**Normal Course of Events:**
1. Admin opens the admin login page directly.
2. Admin enters email and password.
3. Admin presses "Login as Administrator".
4. Admin sees the admin dashboard.

**Alternative Courses:**
- 3.AC.1. Email or password is empty → Admin sees "Email and password are required."
- 3.AC.2. Credentials are incorrect → Admin sees "Invalid email or password."

**Special Requirements:**
- Admin cannot register through any UI form. Account is created by CLI only.
- Admin role does not appear in the staff login role dropdown.

---

### UC-5: Logout

**Actor:** Any authenticated user
**Priority:** High

**Preconditions:**
- PRE-1. User is logged in.

**Postconditions:**
- POST-1. User session is ended. User is taken to the home page.

**Normal Course of Events:**
1. User presses the logout link in the navigation bar.
2. User is taken to the home page and sees the login options.

**Alternative Courses:** None
**Exceptions:** None

---

### UC-6: Password Reset

**EMPTY** — No UI for password reset exists. The feature is not accessible to users.

---

### UC-7: Login via E-Devlet

**EMPTY** — No E-Devlet login button or flow exists in the UI.

---

## 2. Applicant Use Cases

### UC-8: Submit Application

**Actor:** Applicant
**Priority:** High | **Frequency:** Once per applicant

**Preconditions:**
- PRE-1. Applicant is logged in.
- PRE-2. Submission period is open (controlled by a feature flag).
- PRE-3. Applicant has not already submitted an application.

**Postconditions:**
- POST-1. Application is recorded with status "submitted".
- POST-2. Uploaded documents are stored.

**Normal Course of Events:**
1. Applicant opens the "Submit Application" tab on the dashboard.
2. Applicant sees the submission form.
3. Applicant fills in full name, ID number, source university, currently-enrolled status, target program, target semester, and current GPA.
4. Applicant uploads the required documents: Student Certificate, Transcript, YKS Score Report. English Proficiency Certificate is optional.
5. Applicant presses "Submit Application".
6. Applicant sees a success message and is returned to the dashboard.

**Alternative Courses:**
- 1.AC.1. Submission period is closed → Applicant sees the form is unavailable and a "period is closed" notice.
- 5.AC.1. A required form field is missing → Applicant sees a validation error and stays on the form.
- 5.AC.2. A required document slot has no file → Applicant sees a validation error and stays on the form.
- 5.AC.3. Applicant already has a submitted application → Applicant sees a duplicate application error.

**Exceptions:**
- 5.EX.1. File storage or database error → Applicant sees an error message; no application is saved.

**Not Implemented:**
- Automated content validation of uploaded documents.

---

### UC-9: Track Application Status

**Actor:** Applicant
**Priority:** Medium | **Frequency:** Multiple times

**Preconditions:**
- PRE-1. Applicant is logged in.

**Postconditions:**
- POST-1. Applicant sees their current application stage.

**Normal Course of Events:**
1. Applicant opens the "Track Application" tab on the dashboard.
2. Applicant sees a step tracker displaying the pipeline stages: Application Submitted → Initial Verification → Forwarding to Dean's Office → Under Departmental Review → Intibak Process → Result Announcement.
3. Applicant sees the current active step highlighted.

**Alternative Courses:**
- 2.AC.1. Applicant has not submitted an application → Applicant sees "No application found." with a link to the submit tab.

**Exceptions:**
- 1.EX.1. Tab fails to load → Applicant sees a toast error notification.

**Not Implemented:**
- Not all statuses map to a displayed tracker step yet (e.g., approved status has no corresponding stage).

---

### UC-10: Resubmit Application

**Actor:** Applicant
**Priority:** Medium | **Frequency:** Low

**Preconditions:**
- PRE-1. Applicant is logged in.
- PRE-2. Applicant's application was returned by OIDB staff.
- PRE-3. Resubmission period is open (controlled by a feature flag).

**Postconditions:**
- POST-1. Application is updated with the new data and documents.
- POST-2. Application status returns to "submitted".

**Normal Course of Events:**
1. Applicant opens the "Submit Application" tab; the form is pre-filled with existing data and shows the OIDB return notes explaining what must be corrected.
2. Applicant updates the relevant fields or replaces documents.
3. Applicant presses "Resubmit Application".
4. Applicant sees a success message.

**Alternative Courses:**
- 3.AC.1. Resubmission period is closed → Applicant sees "Resubmission is not currently allowed."
- 3.AC.2. Application was not returned → Applicant sees "Only returned applications can be resubmitted."

**Exceptions:**
- 3.EX.1. Database or file storage error → Applicant sees an error message.

---

### UC-11: Cancel Application

**Actor:** Applicant
**Priority:** Low | **Frequency:** Low

**Preconditions:**
- PRE-1. Applicant is logged in.
- PRE-2. Applicant has a submitted or returned application.
- PRE-3. Cancellation period is open (controlled by a feature flag).

**Postconditions:**
- POST-1. Application is marked as cancelled.

**Normal Course of Events:**
1. Applicant presses "Cancel Application" on the dashboard panel.
2. Applicant sees a success message confirming the cancellation.

**Alternative Courses:**
- 1.AC.1. Cancellation period is closed → Applicant sees "Cancellation is not currently allowed."
- 1.AC.2. Application is not in a cancellable state → Applicant sees "Only submitted or returned applications can be cancelled."

**Exceptions:**
- 1.EX.1. Database error → Applicant sees an error message.

**Special Requirements:**
- Cancellation is permanent with no undo mechanism in the UI.

---

## 3. OIDB Staff Use Cases

### UC-12: View Application List

**Actor:** OIDB Staff
**Priority:** High | **Frequency:** Once or more per application cycle

**Preconditions:**
- PRE-1. OIDB Staff is logged in.

**Postconditions:**
- POST-1. OIDB Staff sees the list of pending applications.

**Normal Course of Events:**
1. OIDB Staff opens the "Check Documents" tab on the dashboard.
2. OIDB Staff sees a paginated table of applications with applicant name, status, GPA, target program, and action buttons.
3. Staff presses the expand button on a row to see full applicant details and document links.

**Alternative Courses:**
- 2.AC.1. No pending applications exist → Staff sees an empty table with a corresponding message.

**Exceptions:**
- 1.EX.1. Tab fails to load → Staff sees a toast error notification.

---

### UC-13: View Application Document

**Actor:** OIDB Staff
**Priority:** High | **Frequency:** Multiple per application

**Preconditions:**
- PRE-1. OIDB Staff is logged in.
- PRE-2. Staff has expanded an application row and sees the document links.

**Postconditions:**
- POST-1. The PDF document opens inline in the browser.

**Normal Course of Events:**
1. Staff presses a document link in the expanded application row.
2. Staff sees the PDF document displayed inline in the browser.

**Alternative Courses:** None

**Exceptions:**
- 1.EX.1. Document does not exist → Staff sees a 404 error page.

---

### UC-14: Return Application

**Actor:** OIDB Staff
**Priority:** High | **Frequency:** Per rejected application

**Preconditions:**
- PRE-1. OIDB Staff is logged in.
- PRE-2. The application has not yet been forwarded.

**Postconditions:**
- POST-1. Application is marked as returned.
- POST-2. Return notes are saved and visible to the applicant.

**Normal Course of Events:**
1. Staff presses "Return" on an application row.
2. Staff enters the reason for returning the application in the text field.
3. Staff presses "Submit".
4. Staff sees a success message and the application is removed from the pending list.

**Alternative Courses:**
- 3.AC.1. Return reason field is empty → Staff sees "A reason is required when returning an application."

**Exceptions:**
- 3.EX.1. Application is in a state that cannot be returned → Staff sees an invalid status error message.
- 3.EX.2. Database error → Staff sees an error message.

---

### UC-15: Forward Application to YDYO

**Actor:** OIDB Staff
**Priority:** High | **Frequency:** Per eligible application

**Preconditions:**
- PRE-1. OIDB Staff is logged in.
- PRE-2. Application is pending (submitted or returned state).

**Postconditions:**
- POST-1. Application is forwarded to YDYO and removed from the OIDB pending list.

**Normal Course of Events:**
1. Staff presses "Forward to YDYO" on an application row.
2. Staff sees a success message and the application disappears from the pending list.

**Alternative Courses:**
- 1.AC.1. Staff presses "Forward All to YDYO" → All currently pending applications are forwarded at once and staff sees a batch success message.

**Exceptions:**
- 1.EX.1. Application is in a state that cannot be forwarded → Staff sees an invalid status error message.
- 1.EX.2. Database error → Staff sees an error message and no changes are made.

---

### UC-16: Cancel Forward to YDYO

**Actor:** OIDB Staff
**Priority:** Low | **Frequency:** Low

**Preconditions:**
- PRE-1. OIDB Staff is logged in.
- PRE-2. Application was forwarded to YDYO but YDYO has not yet acted on it.

**Postconditions:**
- POST-1. Application is reverted to the OIDB pending list.

**Normal Course of Events:**
1. Staff presses "Cancel Forward" on a forwarded application row.
2. Staff sees a success message and the application reappears in the pending list.

**Exceptions:**
- 1.EX.1. YDYO has already acted on the application → Staff sees "Cancellation is only possible while still forwarded to YDYO."

---

### UC-17: Create Waitlist Table

**EMPTY** — The "Create Waitlist Table" tab exists on the OIDB dashboard but has no implemented functionality.

---

## 4. YDYO Staff Use Cases

### UC-18: View Applications Forwarded to YDYO

**Actor:** YDYO Staff
**Priority:** High | **Frequency:** Once or more per cycle

**Preconditions:**
- PRE-1. YDYO Staff is logged in.

**Postconditions:**
- POST-1. YDYO Staff sees the applications awaiting English prep review.

**Normal Course of Events:**
1. YDYO Staff opens the "Set Prep School Status" tab on the dashboard.
2. YDYO Staff sees a list of applications with applicant name, GPA, target program, and document links.

**Alternative Courses:**
- 2.AC.1. No applications are waiting → Staff sees an empty list.

**Exceptions:**
- 1.EX.1. Tab fails to load → Staff sees a toast error notification.

---

### UC-19: Mark English Prep Status and Forward to Dean

**Actor:** YDYO Staff
**Priority:** High | **Frequency:** Once per application

**Preconditions:**
- PRE-1. YDYO Staff is logged in.
- PRE-2. Application is in the YDYO queue.

**Postconditions:**
- POST-1. English prep school status is recorded on the application.
- POST-2. Application is forwarded to the Dean's Office.

**Normal Course of Events:**
1. Staff expands an application row.
2. Staff selects the applicant's English prep status from the dropdown (eligible / needs test).
3. Staff presses "Save and Forward".
4. Staff sees a success message and the application disappears from the list.

**Alternative Courses:**
- 2.AC.1. Staff presses "Forward All to Dean" → All applications in the YDYO queue are forwarded at once and staff sees a batch success message.

**Exceptions:**
- 3.EX.1. Database error → Staff sees an error message; application status is not changed.

---

### UC-20: View Application Document (YDYO)

**Actor:** YDYO Staff
**Priority:** Medium

**Preconditions:**
- PRE-1. YDYO Staff is logged in.
- PRE-2. Staff has an application row expanded showing document links.

**Postconditions:**
- POST-1. The PDF document opens inline in the browser.

**Normal Course of Events:**
1. Staff presses a document link in the expanded application row.
2. Staff sees the PDF document displayed inline in the browser.

**Exceptions:**
- 1.EX.1. Document does not exist → Staff sees a 404 error page.

---

## 5. Dean's Office Use Cases

### UC-21: View Applications Forwarded to Dean

**Actor:** Dean
**Priority:** High | **Frequency:** Once per cycle

**Preconditions:**
- PRE-1. Dean is logged in.

**Postconditions:**
- POST-1. Dean sees the applications that have passed YDYO review.

**Normal Course of Events:**
1. Dean opens the "Receive & Forward Applications" tab on the dashboard.
2. Dean sees a list of applications with applicant details, GPA, English prep status, and action buttons.

**Alternative Courses:**
- 2.AC.1. No applications are waiting → Dean sees an empty table.

---

### UC-22: Forward Application to YGK

**Actor:** Dean
**Priority:** High | **Frequency:** Per eligible application

**Preconditions:**
- PRE-1. Dean is logged in.
- PRE-2. Application is in the Dean's queue.

**Postconditions:**
- POST-1. Application is forwarded to the appropriate YGK with the faculty assignment recorded.

**Normal Course of Events:**
1. Dean expands an application row.
2. Dean selects the target faculty from the dropdown.
3. Dean presses "Forward to YGK".
4. Dean sees a success message and the application is removed from the list.

**Alternative Courses:**
- 3.AC.1. No faculty is selected → Dean sees "A faculty must be selected before forwarding."

**Exceptions:**
- 3.EX.1. Application is in a state that cannot be forwarded → Dean sees an invalid status error message.
- 3.EX.2. Database error → Dean sees an error message.

**Not Implemented:**
- "Forward All to YGK" button exists but pressing it shows a "not yet implemented" error.

---

## 6. YGK Use Cases

### UC-23: View Applications Forwarded to YGK

**Actor:** YGK
**Priority:** High

**Preconditions:**
- PRE-1. YGK staff is logged in.

**Postconditions:**
- POST-1. YGK sees the applications assigned to them with faculty and applicant details.

**Normal Course of Events:**
1. YGK opens the "Check Applicants" tab on the dashboard.
2. YGK sees the list of applications with faculty assignment and applicant details.

**Alternative Courses:**
- 2.AC.1. No applications are assigned → YGK sees an empty list.

---

### UC-24: Approve Application

**Actor:** YGK
**Priority:** High

**Preconditions:**
- PRE-1. YGK staff is logged in.
- PRE-2. Application is in the YGK queue.

**Postconditions:**
- POST-1. Application is marked as approved.

**Normal Course of Events:**
1. YGK presses "Approve" on an application row.
2. YGK sees a success message and is returned to the applicant list.

**Exceptions:**
- 1.EX.1. Database error → YGK sees an error message.

**Not Implemented:**
- Rejection flow — no reject action exists.
- Applicant is not notified of the approval result.

---

### UC-25: Create Intibak Table

**EMPTY** — The "Intibak Table" tab exists on the YGK dashboard but has no implemented functionality.

---

## 7. Admin Use Cases

### UC-26: View All Users and Change Role

**Actor:** Admin
**Priority:** High

**Preconditions:**
- PRE-1. Admin is logged in.

**Postconditions:**
- POST-1. Target user's role is updated.

**Normal Course of Events:**
1. Admin opens the "User Management" tab on the dashboard.
2. Admin sees a list of all users with their current roles.
3. Admin selects a new role from the dropdown next to a user and presses "Change Role".
4. Admin sees a success message confirming the role update.

**Alternative Courses:**
- 3.AC.1. The selected role is not a valid assignable role → Admin sees an error message.

**Exceptions:**
- 3.EX.1. Target user not found → Admin sees "User not found."
- 3.EX.2. Database error → Admin sees an error message.

---

### UC-27: View Config Flags

**Actor:** Admin
**Priority:** Low

**Preconditions:**
- PRE-1. Admin is logged in.

**Postconditions:**
- POST-1. Admin sees the current state of all feature flags.

**Normal Course of Events:**
1. Admin opens the "Config" tab on the dashboard.
2. Admin sees the current values of all feature flags (submission period, cancellation, resubmission).

**Alternative Courses:** None — read-only view, no editing through the UI.

---

### UC-28: Create Database Backup

**Actor:** Admin
**Priority:** Medium

**Preconditions:**
- PRE-1. Admin is logged in.

**Postconditions:**
- POST-1. A timestamped backup of the database is saved.

**Normal Course of Events:**
1. Admin opens the "Database" tab and presses "Create Backup".
2. Admin sees a success message showing the name of the created backup file.

**Exceptions:**
- 1.EX.1. File system error → Admin sees an error message; no backup is created.

---

### UC-29: Restore Database from Backup

**Actor:** Admin
**Priority:** Medium

**Preconditions:**
- PRE-1. Admin is logged in.
- PRE-2. At least one backup file exists.

**Postconditions:**
- POST-1. The live database is replaced with the selected backup.

**Normal Course of Events:**
1. Admin opens the "Database" tab and sees the list of available backups with timestamps and sizes.
2. Admin selects a backup from the list and presses "Restore".
3. Admin sees a success message confirming the restore.

**Alternative Courses:**
- 2.AC.1. The backup filename fails security validation → Admin sees a validation error and no restore is performed.

**Exceptions:**
- 2.EX.1. Backup file not found → Admin sees "Backup file not found."
- 2.EX.2. File system error during restore → Admin sees an error message.

---

## Summary of Empty / Not-Implemented Areas

| Feature | Status |
|---|---|
| Email confirmation on register | Not implemented — registration is immediate |
| Password reset | Not accessible — no UI route |
| E-Devlet / SSO login | Not implemented |
| Automated document content check | Not implemented |
| YGK Intibak table creation | Empty tab — no functionality |
| Dean "Forward All to YGK" | Button exists but always returns an error |
| OIDB waitlist / asil-yedek table | Empty tab — no functionality |
| Result notification to applicants | Not implemented |
