# Global Architecture & Development Rules

## 1. Tech Stack
* **Backend:** Flask (Python)
* **Database:** SQLAlchemy ORM (Currently SQLite, MUST be architected for seamless migration to PostgreSQL).
* **Methodology:** Agile. We are currently in the "Shell/Baseline" phase.

## 2. Directory Structure Rules
Code must be strictly modular. Do not put everything in `app.py`.
* `/app/routes/`: Blueprint definitions separated by role (e.g., `applicant.py`, `dean.py`).
* `/app/models/`: SQLAlchemy database models.
* `/app/classes/`: Core business logic and OOP classes (separated from routes).
* `/app/database/`: Database interface and abstraction layers.

## 3. Database Abstraction (Critical)
* Never execute raw SQL queries directly in route functions.
* All database interactions must pass through a `DatabaseInterface` abstraction.
* This interface must handle: `Connect`, `Disconnect`, `ExecuteQuery` (with parameter binding to prevent injection), and `Backup`.
* Implement a `DatabaseControlInterface` to restrict dangerous operations and reduce redundancy.

## 4. Single Source of Truth
* This specification defines the *structure* and *rules*. 
* If the existing Python code deviates from this document in method implementations, treat the Python codebase as the source of truth, but enforce the structural rules defined here.