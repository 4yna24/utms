"""Database layer interfaces with two-tier architecture."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..core import OperationResult, ErrorCode


class ILowLevelDatabase(ABC):
    """
    Low-level database abstraction for raw operations.

    Handles basic connection, query execution, and housekeeping.
    No business logic — just execute and get results.
    """

    @abstractmethod
    def execute_query(self, action_name: str, payload: dict[str, Any] | None = None) -> OperationResult:
        """Execute a named data action. Returns OperationResult with data or error."""

    @abstractmethod
    def connect(self) -> OperationResult:
        """Open a database connection if required."""

    @abstractmethod
    def disconnect(self) -> OperationResult:
        """Close a database connection if required."""

    @abstractmethod
    def backup(self) -> OperationResult:
        """Create a database backup artifact."""


class IHighLevelDatabase(ABC):
    """
    High-level database operations using ILowLevelDatabase.

    Handles complex queries, transactions, and business-specific data access.
    Uses ILowLevelDatabase internally to maintain separation of concerns.
    """

    @abstractmethod
    def safe_execute(
        self, action_name: str, payload: dict[str, Any] | None = None
    ) -> OperationResult:
        """
        Execute only whitelisted named actions with validation.

        Enforces allowed actions and returns rich OperationResult.
        """


class IUserRepository(ABC):
    """
    User persistence interface (high-level user operations).

    Wraps database operations for finding/creating/managing users.
    All methods return OperationResult with error codes.
    """

    @abstractmethod
    def find_by_email_and_role(self, email: str, role: str) -> OperationResult:
        """
        Find user by email and role.

        Returns OperationResult with User data or NOT_FOUND error.
        """

    @abstractmethod
    def create_user(
        self, email: str, password: str, role: str, check_user_validity: bool = True
    ) -> OperationResult:
        """
        Create and return a user.

        Returns OperationResult with created User or error:
        - DUPLICATE_EMAIL_ROLE if user exists
        - DB_ERROR if creation fails
        """

    @abstractmethod
    def find_by_id(self, user_id: int) -> OperationResult:
        """
        Find user by ID.

        Returns OperationResult with User data or NOT_FOUND error.
        """


# Legacy aliases (deprecated, kept for backward compatibility during migration)
DatabaseInterface = ILowLevelDatabase
DatabaseControlInterface = IHighLevelDatabase
UserDataInterface = IUserRepository
