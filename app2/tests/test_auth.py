"""Authentication route tests."""

import pytest


class TestPublicPages:
    def test_home_page_loads(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"UTMS" in resp.data or b"portal" in resp.data.lower()

    def test_applicant_portal_entry_redirects(self, client):
        resp = client.get("/portals/applicant/", follow_redirects=False)
        assert resp.status_code == 302
        assert "auth" in resp.location.lower()

    def test_staff_portal_entry_redirects(self, client):
        for role in ("dean", "oidb", "ydyo", "ygk"):
            resp = client.get(f"/portals/{role}/", follow_redirects=False)
            assert resp.status_code == 302
            assert "auth" in resp.location.lower()

    def test_applicant_login_page_renders(self, client):
        resp = client.get("/auth/applicant/login")
        assert resp.status_code == 200
        assert b"email" in resp.data.lower() or b"login" in resp.data.lower()

    def test_applicant_register_page_renders(self, client):
        resp = client.get("/auth/applicant/register")
        assert resp.status_code == 200

    def test_staff_login_page_renders(self, client):
        resp = client.get("/auth/staff/login")
        assert resp.status_code == 200

    def test_dashboard_blocked_without_login(self, client):
        resp = client.get("/dashboard/", follow_redirects=False)
        assert resp.status_code == 302
        assert "login" in resp.location.lower() or "auth" in resp.location.lower()


class TestLoginFlow:
    def test_valid_applicant_login(self, client, applicant_user):
        resp = client.post(
            "/auth/applicant/login",
            data={"email": applicant_user.email, "password": "test"},
            follow_redirects=False,
        )
        assert resp.status_code == 302
        assert "dashboard" in resp.location.lower()

    def test_wrong_password_rejected(self, client, applicant_user):
        resp = client.post(
            "/auth/applicant/login",
            data={"email": applicant_user.email, "password": "wrong"},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        content = resp.data.lower()
        assert b"invalid" in content or b"incorrect" in content or b"error" in content

    def test_unknown_email_rejected(self, client):
        resp = client.post(
            "/auth/applicant/login",
            data={"email": "nobody@nowhere.com", "password": "test"},
            follow_redirects=True,
        )
        assert resp.status_code == 200


class TestSessionManagement:
    def test_session_set_after_login(self, auth_client_applicant):
        with auth_client_applicant.session_transaction() as sess:
            assert sess.get("user_id") is not None
            assert sess.get("user_role") == "applicant"

    def test_authenticated_user_redirected_from_login(self, auth_client_applicant):
        resp = auth_client_applicant.get("/auth/applicant/login", follow_redirects=False)
        assert resp.status_code == 302
        assert "dashboard" in resp.location.lower()

    def test_authenticated_user_redirected_from_register(self, auth_client_applicant):
        resp = auth_client_applicant.get("/auth/applicant/register", follow_redirects=False)
        assert resp.status_code == 302

    def test_logout_clears_session(self, auth_client_applicant):
        resp = auth_client_applicant.get("/auth/logout", follow_redirects=False)
        assert resp.status_code == 302
        with auth_client_applicant.session_transaction() as sess:
            assert sess.get("user_id") is None
