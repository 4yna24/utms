# Domain Models & Business Logic Classes

## 1. Users
* **User:** SQLAlchemy authentication model.
    * Attributes: `id`, `email`, `role`, `password_hash`.
    * Relationship: one optional `Application`.

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
    * SQLAlchemy model for applicant submissions.
    * Attributes: `id`, `applicant_id`, `full_name`, `student_number`, `source_university`, `target_department`, `current_gpa`, `status`, `created_at`.
    * Relationship: one `User`, many `ApplicationDocument` rows.
* **ApplicationDocument:**
    * SQLAlchemy model for uploaded submission files.
    * Attributes: `id`, `application_id`, `document_slot`, `original_name`, `stored_name`, `file_path`, `created_at`.
    * Supports document slots `1..4`.
* **Document:** legacy business-layer concept now represented by `ApplicationDocument` in the database layer.
* **IntibakTable:** Represents course equivalency matrices.

*Rule: Use abstract interfaces for common methods across these classes to reduce redundancy.*

## 5. Interface Abstractions (Extensibility)
To maintain the DRY principle, use Abstract Base Classes (`abc.ABC`) for shared role capabilities.

* **`IReviewer` Interface:** * Methods: `get_pending_applicants()`, `update_applicant_status()`
    * Implemented by: `DeanOffice`, `Oidb`, `Ydyo`, `YGK`
* **`IDocumentHandler` Interface:**
    * Methods: `upload()`, `validate()`, `retrieve()`
    * Implemented by: `Applicant`, `Oidb`

*Note: You are authorized to expand these interfaces or add internal helper methods to the core classes to keep the implementation clean and modular. In the current code, `Application` and `ApplicationDocument` are the primary persisted entities for submission handling.*