from abc import ABC, abstractmethod


class DatabaseInterface(ABC):
    """Low-level database abstraction."""

    @abstractmethod
    def execute_query(self, action_name, payload=None):
        """Execute a named data action."""

    @abstractmethod
    def connect(self):
        """Open a database connection if required."""

    @abstractmethod
    def disconnect(self):
        """Close a database connection if required."""

    @abstractmethod
    def backup(self):
        """Create a database backup artifact."""


class DatabaseControlInterface(ABC):
    """Restrict and centralize dangerous DB operations."""

    @abstractmethod
    def safe_execute(self, action_name, payload=None):
        """Execute only whitelisted named actions."""


class UserDataInterface(ABC):
    """User persistence abstraction."""

    @abstractmethod
    def find_by_email_role(self, email, role):
        """Return a user by role-specific identity, or None."""

    @abstractmethod
    def create_user(self, email, password, role, check_user_validity: bool = True):
        """Create and return a user."""

    @abstractmethod
    def find_by_id(self, user_id):
        """Return user by id or None."""
