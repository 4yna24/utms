# Global Architecture & Development Rules

## 1. Tech Stack
* **Backend:** Flask (Python)
* **Database:** SQLAlchemy ORM (Currently SQLite, but the data model should remain migration-friendly).
* **Methodology:** Agile.

## 2. Directory Structure Rules
Code must be strictly modular. Do not put everything in `app.py`.
* `/app/routes/`: Blueprint definitions separated by role and feature area (e.g., `applicant.py`, `oidb.py`, `dashboard.py`).
* `/app/models/`: SQLAlchemy database models.
* `/app/classes/`: Core business logic and OOP classes (separated from routes).
* `/app/database/`: Database interface and abstraction layers.
* `/app/templates/`: Workspace and role UI rendered server-side.

## 3. Database Abstraction (Critical)
* Never execute raw SQL queries directly in route functions.
* All database interactions should pass through a `DatabaseInterface` abstraction where the project already uses it.
* This interface must handle: `Connect`, `Disconnect`, `ExecuteQuery` (with parameter binding to prevent injection), and `Backup`.
* Implement a `DatabaseControlInterface` to restrict dangerous operations and reduce redundancy.
* Keep route logic thin. Routes should validate input, load data, and hand off rendering or persistence to the proper layer.

## 4. Single Source of Truth
* This specification defines the *structure* and *rules*.
* If the existing Python code deviates from this document in method implementations, treat the Python codebase as the source of truth, but keep the documented structure updated to match the working system.