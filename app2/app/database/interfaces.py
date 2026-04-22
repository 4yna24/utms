from abc import ABC, abstractmethod


class DatabaseInterface(ABC):
    @abstractmethod
    def execute_query(self, action_name, payload=None):
        """Execute a named data action."""

    def connect(self):
        pass

    def disconnect(self):
        pass

    def backup(self):
        pass


class UserDataInterface(ABC):
    @abstractmethod
    def find_by_email_role(self, email, role):
        """Return a user by role-specific identity, or None."""

    @abstractmethod
    def create_user(self, email, password, role):
        """Create and return a user."""
