"""Authentication tests."""

import pytest


class TestAuthRoutes:
    """Test authentication routes."""

    def test_home_page_loads(self, client):
        """Test home page is accessible."""
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"UTMS" in resp.data or b"portal" in resp.data.lower()

    def test_role_entry_applicant(self, client):
        """Test role entry redirects applicant to login."""
        resp = client.get("/portals/applicant/", follow_redirects=False)
        assert resp.status_code == 302
        assert "auth" in resp.location.lower()

    def test_role_entry_dean(self, client):
        """Test role entry redirects dean to staff login."""
        resp = client.get("/portals/dean/", follow_redirects=False)
        assert resp.status_code == 302
        assert "auth" in resp.location.lower()

    def test_role_entry_oidb(self, client):
        """Test role entry redirects OIDB to staff login."""
        resp = client.get("/portals/oidb/", follow_redirects=False)
        assert resp.status_code == 302
        assert "auth" in resp.location.lower()

    def test_login_page_get(self, client):
        """Test login page renders."""
        resp = client.get("/auth/applicant/login")
        assert resp.status_code == 200
        assert b"login" in resp.data.lower() or b"email" in resp.data.lower()

    def test_register_page_get(self, client):
        """Test register page renders."""
        resp = client.get("/auth/applicant/register")
        assert resp.status_code == 200
        assert b"register" in resp.data.lower() or b"email" in resp.data.lower()

    def test_authenticated_user_redirected_from_login(self, auth_client_applicant):
        """Test authenticated user is redirected away from login."""
        resp = auth_client_applicant.get("/auth/applicant/login", follow_redirects=False)
        assert resp.status_code == 302
        assert "dashboard" in resp.location.lower()

    def test_authenticated_user_redirected_from_register(self, auth_client_applicant):
        """Test authenticated user is redirected away from register."""
        resp = auth_client_applicant.get("/auth/applicant/register", follow_redirects=False)
        assert resp.status_code == 302
        assert "dashboard" in resp.location.lower()


class TestSessionManagement:
    """Test session handling."""

    def test_session_set_on_login(self, auth_client_applicant):
        """Test session is properly set for authenticated user."""
        with auth_client_applicant.session_transaction() as sess:
            assert sess.get("user_id") is not None
            assert sess.get("user_email") is not None
            assert sess.get("user_role") == "applicant"

    def test_unauthenticated_user_no_session(self, client):
        """Test unauthenticated user has no session."""
        with client.session_transaction() as sess:
            assert sess.get("user_id") is None
