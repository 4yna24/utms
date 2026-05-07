"""Authentication business logic class."""

from __future__ import annotations

from typing import Any

from ..database import get_user_data_interface


class AuthClass:
    """Encapsulates authentication use cases."""

    def validate_credentials(
        self,
        email: str,
        password: str,
        role: str | None = None,
        valid_roles: set[str] | None = None,
    ) -> tuple[bool, str]:
        """Return (True, "") when fields are present and role is valid."""
        if not email or not password:
            return False, "All fields are required."
        if role is not None and valid_roles is not None and role not in valid_roles:
            return False, "All fields are required and role must be a valid role."
        return True, ""

    def authenticate_user(self, email: str, password: str, role: str):
        """Return matching user when credentials are valid."""
        user_data = get_user_data_interface()
        user = user_data.find_by_email_role(email=email, role=role)
        if user and user.check_password(password):
            return user
        return None

    def register_user(self, email: str, password: str, role: str, check_user_validity: bool = True):
        """Create user if a role-scoped email does not exist."""
        user_data = get_user_data_interface()
        if check_user_validity:
            existing_user = user_data.find_by_email_role(email=email, role=role)
            if existing_user:
                return None
        return user_data.create_user(
            email=email,
            password=password,
            role=role,
            check_user_validity=check_user_validity,
        )

    def send_confirmation_email(self, email: str) -> bool:
        """Phase 1 placeholder for email confirmation."""
        return bool(email)

    def request_password_reset(self, email: str) -> dict[str, Any]:
        """Phase 1 placeholder for reset flow."""
        return {"email": email, "status": "requested"}

    def reset_password(self, email: str, new_password: str) -> bool:
        """Phase 1 placeholder for password reset."""
        return bool(email and new_password)

    def login_with_edevlet(self, token: str) -> dict[str, str]:
        """Phase 1 placeholder for e-Devlet integration."""
        return {"token": token, "status": "not_implemented"}
