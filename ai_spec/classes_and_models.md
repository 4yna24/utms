# Domain Models & Business Logic Classes

## 1. Abstract Users
* **User (Abstract Class):** * Attributes: `UserID`, `Email`, `PasswordHash`, `Role`.
    * Methods: `login()`, `logout()`, `getID()`.

## 2. Authentication
* **AuthClass:**
    * Methods: `authenticate_user()`, `register_user()`, `send_confirmation_email()`, `request_password_reset()`, `reset_password()`, `login_with_edevlet()`.

## 3. Role Implementations (Business Logic)
* **Applicant:** `submit_document()`, `track_document()`, `cancel_application()`, `resubmit_documents()`.
* **DeanOffice:** `receive_documents()`, `forward_documents()`.
* **YGK:** `create_intibak_table()`, `edit_course_match()`, `save_intibak_table()`.
* **Oidb:** `retrieve_documents()`, `edit_documents()`, `create_waitlist_table()`.
* **Ydyo:** `retrieve_applications()`, `set_prepschool_status()`.

## 4. Core Entities
* **Application:**
    * Attributes: `ApplicationID`, `SubmissionDate`, `Status`, `StudentID`, `TargetID`.
* **Document:** Class holding file metadata and status; owned by Applicant.
* **IntibakTable:** Represents course equivalency matrices.

*Rule: Use abstract interfaces for common methods across these classes to reduce redundancy.*

## 5. Interface Abstractions (Extensibility)
To maintain the DRY principle, use Abstract Base Classes (`abc.ABC`) for shared role capabilities.

* **`IReviewer` Interface:** * Methods: `get_pending_applicants()`, `update_applicant_status()`
    * Implemented by: `DeanOffice`, `Oidb`, `Ydyo`, `YGK`
* **`IDocumentHandler` Interface:**
    * Methods: `upload()`, `validate()`, `retrieve()`
    * Implemented by: `Applicant`, `Oidb`

*Note: You are authorized to expand these interfaces or add internal helper methods to the core classes to keep the implementation clean and modular.*