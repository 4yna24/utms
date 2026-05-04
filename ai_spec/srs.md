

# UTMS — Use Case Status (SRS)

This file tracks implementation status and UI placement notes for each use case.

## Applicant

1. **UC-1** — Register to system *(Applicant)* — **DONE**
2. **UC-2** — Log in *(Applicant)* — **DONE**
3. **UC-3** — Reset the password *(Applicant)* — **IGNORE**
4. **UC-4** — Submit the documents *(Applicant)* — **TODO**
5. **UC-5** — Track Results *(Applicant)* — **TODO**
6. **UC-6** — Update Documents *(Applicant)* — **TODO**
7. **UC-23** — Resubmit Documents *(Applicant)* — **TODO**
8. **UC-21** — Applicant cancels application *(Applicant)* — **TODO**

**UI note:** Use cases **UC-5**, **UC-6**, **UC-23**, **UC-21** live under the **Track Results** tab. In **Track Results**, the applicant may have options to **resubmit**, **update**, or **cancel**.

## Dean

9. **UC-7** — Receive applications *(Dean)* — **TODO**
10. **UC-8** — Forward application *(Dean)* — **TODO**
11. **UC-24** — Login *(Dean)* — **DONE**

**UI note:** Use cases **UC-7** and **UC-8** share one page. Receiving/seeing applications is the **Dashboard** tab, and it includes buttons to forward to the respective faculty.

## YGK

12. **UC-18** — Create the intibak tables *(YGK)* — **IGNORE**
13. **UC-25** — Login *(YGK)* — **DONE**

## OIDB

14. **UC-19** — Retrieve documents *(OIDB)* — **TODO**
15. **UC-20** — Create waitlist tables *(OIDB)* — **TODO (last)**
16. **UC-26** — Login *(OIDB)* — **DONE**
17. **UC-27** — Check documents *(OIDB)* — **TODO**

**UI note:** Use cases **UC-19**, **UC-20**, **UC-27** share the same screen/tab:

- A screen with applications.
- Top-right button to check validity for **all documents**.
- OIDB staff can expand an application block and manually check each field, find errors, mark an application as bad, send it back, and notify the applicant.
