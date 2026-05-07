

# UTMS — Use Case Status (SRS)

This file tracks implementation status and UI placement notes for each use case.

## Applicant

1. **UC-1** — Register to system *(Applicant)* — **DONE**
2. **UC-2** — Log in *(Applicant)* — **DONE**
3. **UC-3** — Reset the password *(Applicant)* — **IGNORE**
4. **UC-4** — Submit the documents *(Applicant)* — **DONE**
5. **UC-5** — Track Results *(Applicant)* — **DONE**
6. **UC-6** — Update Documents *(Applicant)* — **DONE**
7. **UC-23** — Resubmit Documents *(Applicant)* — **DONE**
8. **UC-21** — Applicant cancels application *(Applicant)* — **TODO**

**UI note:** Use cases **UC-5**, **UC-6**, **UC-23**, **UC-21** live under the **Track Results** tab. In **Track Results**, the applicant may have options to **resubmit**, **update**, or **cancel**.

## Dean

9. **UC-7** — Receive applications *(Dean)* — **DONE**
10. **UC-8** — Forward application to departmental YGK *(Dean)* — **DONE**
11. **UC-24** — Login *(Dean)* — **DONE**

**UI note:** Use cases **UC-7** and **UC-8** share one page. Dean expands an application, selects the target faculty from a dropdown, and clicks **Forward to YGK** — this records `forwarded_faculty` and transitions status to `forwarded_to_ygk`. The **Forward All to YGK** button is a placeholder (no logic yet). After forwarding, the row shows the selected faculty name in place of the action controls.

## YGK

12. **UC-18** — Create the intibak tables *(YGK)* — **IGNORE**
13. **UC-25** — Login *(YGK)* — **DONE**

## OIDB

14. **UC-19** — Retrieve documents *(OIDB)* — **DONE**
15. **UC-20** — Create waitlist tables *(OIDB)* — **TODO (last)**
16. **UC-26** — Login *(OIDB)* — **DONE**
17. **UC-27** — Check documents *(OIDB)* — **DONE**

**UI note:** Use cases **UC-19**, **UC-20**, **UC-27** share the same screen/tab:

- A screen with applications.
- Top-right button to check validity for **all documents**.
- OIDB staff can expand an application block and manually check each field, find errors, mark an application as bad, send it back, and notify the applicant.

## YDYO

18. **UC-28** — Login *(YDYO)* — **DONE**
19. **UC-29** — Set prep school status *(YDYO)* — **DONE**
20. **UC-30** — Auto-forward all to Dean *(YDYO)* — **TODO (placeholder — button exists, logic not implemented)**

**UI note:** Use cases **UC-29** and **UC-30** share the **Set Prep School Status** tab:

- Shows only applications with status `forwarded_to_ydyo`.
- YDYO staff expands an application and reviews the **English Proficiency Certificate** (document slot 4).
- Staff marks each applicant with one of two decisions:
  - **English Eligible** — applicant's proficiency certificate is accepted; no internal test required.
  - **Needs Internal Test** — applicant must sit the university's internal English examination.
- Marking a decision sets `prep_school_status` on the application (`"eligible"` or `"needs_test"`) and immediately forwards the application to Dean (post-condition).
- The **Forward All to Dean** button is a placeholder; bulk logic is not yet implemented.
