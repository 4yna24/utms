"""Role access, isolation, and OIDB workflow tests."""

import pytest

from app.classes.users.oidb import Oidb
from app.models import ApplicationORM


class TestRoleAccess:
    """Each staff role can reach the dashboard."""

    def test_dean_dashboard(self, auth_client_dean):
        assert auth_client_dean.get("/dashboard/").status_code == 200

    def test_oidb_dashboard(self, auth_client_oidb):
        assert auth_client_oidb.get("/dashboard/").status_code == 200

    def test_ydyo_dashboard(self, auth_client_ydyo):
        assert auth_client_ydyo.get("/dashboard/").status_code == 200

    def test_ygk_dashboard(self, auth_client_ygk):
        assert auth_client_ygk.get("/dashboard/").status_code == 200

    def test_applicant_dashboard(self, auth_client_applicant):
        assert auth_client_applicant.get("/dashboard/").status_code == 200


class TestRoleIsolation:
    """Roles cannot call each other's action endpoints."""

    def test_applicant_cannot_forward_as_oidb(self, auth_client_applicant):
        resp = auth_client_applicant.post("/api/oidb/forward-to-ydyo/1")
        assert resp.status_code in (302, 403)

    def test_applicant_cannot_forward_as_dean(self, auth_client_applicant):
        resp = auth_client_applicant.post("/api/dean/forward-to-ygk/1")
        assert resp.status_code in (302, 403, 404)

    def test_dean_cannot_use_oidb_routes(self, auth_client_dean):
        resp = auth_client_dean.post("/api/oidb/forward-to-ydyo/1")
        assert resp.status_code in (302, 403)

    def test_ydyo_cannot_use_oidb_cancel(self, auth_client_ydyo):
        resp = auth_client_ydyo.post("/api/oidb/cancel-forward-to-ydyo/1")
        assert resp.status_code in (302, 403)


class TestTabContentEndpoint:
    """GET /dashboard/tab/<slug> lazy-load endpoint."""

    def test_oidb_check_documents_tab(self, auth_client_oidb):
        resp = auth_client_oidb.get("/dashboard/tab/check-documents")
        assert resp.status_code == 200

    def test_dean_tab_content(self, auth_client_dean):
        resp = auth_client_dean.get("/dashboard/tab/receive-forward-applications")
        assert resp.status_code == 200

    def test_ydyo_tab_content(self, auth_client_ydyo):
        resp = auth_client_ydyo.get("/dashboard/tab/set-prep-school-status")
        assert resp.status_code == 200

    def test_applicant_track_tab(self, auth_client_applicant):
        resp = auth_client_applicant.get("/dashboard/tab/track-application")
        assert resp.status_code == 200

    def test_invalid_slug_returns_404(self, auth_client_oidb):
        resp = auth_client_oidb.get("/dashboard/tab/this-does-not-exist")
        assert resp.status_code == 404

    def test_tab_content_blocked_without_login(self, client):
        resp = client.get("/dashboard/tab/check-documents", follow_redirects=False)
        assert resp.status_code == 302

    def test_tab_slug_not_owned_by_role_returns_404(self, auth_client_dean):
        # Dean doesn't have a "check-documents" tab
        resp = auth_client_dean.get("/dashboard/tab/check-documents")
        assert resp.status_code == 404

    def test_pagination_param_accepted(self, auth_client_oidb):
        resp = auth_client_oidb.get("/dashboard/tab/check-documents?page=1")
        assert resp.status_code == 200

    def test_pagination_out_of_range_clamped(self, auth_client_oidb):
        resp = auth_client_oidb.get("/dashboard/tab/check-documents?page=999")
        assert resp.status_code == 200


class TestOidbForwardWorkflow:
    """OIDB can forward, return, and cancel-forward applications."""

    def test_forward_to_ydyo_success(self, app, oidb_user, application_submitted):
        with app.app_context():
            oidb = Oidb(oidb_user.id, oidb_user.email, "oidb")
            result = oidb.forward_to_ydyo(application_submitted.id)
            assert result.success
            updated = ApplicationORM.query.get(application_submitted.id)
            assert updated.status == "forwarded_to_ydyo"

    def test_forward_to_ydyo_wrong_status(self, app, oidb_user, application_forwarded_to_ydyo):
        with app.app_context():
            oidb = Oidb(oidb_user.id, oidb_user.email, "oidb")
            result = oidb.forward_to_ydyo(application_forwarded_to_ydyo.id)
            assert not result.success

    def test_return_application_success(self, app, oidb_user, application_submitted):
        with app.app_context():
            oidb = Oidb(oidb_user.id, oidb_user.email, "oidb")
            result = oidb.return_application(application_submitted.id, "Missing transcript.")
            assert result.success
            updated = ApplicationORM.query.get(application_submitted.id)
            assert updated.status == "returned"
            assert updated.oidb_notes == "Missing transcript."

    def test_return_application_requires_notes(self, app, oidb_user, application_submitted):
        with app.app_context():
            oidb = Oidb(oidb_user.id, oidb_user.email, "oidb")
            result = oidb.return_application(application_submitted.id, "")
            assert not result.success

    def test_return_application_wrong_status(self, app, oidb_user, application_forwarded_to_ydyo):
        with app.app_context():
            oidb = Oidb(oidb_user.id, oidb_user.email, "oidb")
            result = oidb.return_application(application_forwarded_to_ydyo.id, "Some reason.")
            assert not result.success

    def test_cancel_forward_to_ydyo_success(self, app, oidb_user, application_forwarded_to_ydyo):
        with app.app_context():
            oidb = Oidb(oidb_user.id, oidb_user.email, "oidb")
            result = oidb.cancel_forward_to_ydyo(application_forwarded_to_ydyo.id)
            assert result.success
            updated = ApplicationORM.query.get(application_forwarded_to_ydyo.id)
            assert updated.status == "submitted"

    def test_cancel_forward_to_ydyo_wrong_status(self, app, oidb_user, application_submitted):
        with app.app_context():
            oidb = Oidb(oidb_user.id, oidb_user.email, "oidb")
            result = oidb.cancel_forward_to_ydyo(application_submitted.id)
            assert not result.success
            assert "ydyo" in result.error_msg.lower()

    def test_cancel_forward_nonexistent(self, app, oidb_user):
        with app.app_context():
            oidb = Oidb(oidb_user.id, oidb_user.email, "oidb")
            result = oidb.cancel_forward_to_ydyo(99999)
            assert not result.success


class TestOidbRoutes:
    """HTTP layer for OIDB actions redirects to dashboard with tab param."""

    def test_forward_route_redirects_to_dashboard(
        self, auth_client_oidb, application_submitted
    ):
        resp = auth_client_oidb.post(
            f"/api/oidb/forward-to-ydyo/{application_submitted.id}",
            follow_redirects=False,
        )
        assert resp.status_code == 302
        assert "dashboard" in resp.location.lower()
        assert "tab=check-documents" in resp.location

    def test_return_route_redirects_to_dashboard(
        self, auth_client_oidb, application_submitted
    ):
        resp = auth_client_oidb.post(
            f"/api/oidb/return-application/{application_submitted.id}",
            data={"oidb_notes": "Documents missing."},
            follow_redirects=False,
        )
        assert resp.status_code == 302
        assert "dashboard" in resp.location.lower()
        assert "tab=check-documents" in resp.location

    def test_cancel_forward_route_redirects_to_dashboard(
        self, auth_client_oidb, application_forwarded_to_ydyo
    ):
        resp = auth_client_oidb.post(
            f"/api/oidb/cancel-forward-to-ydyo/{application_forwarded_to_ydyo.id}",
            follow_redirects=False,
        )
        assert resp.status_code == 302
        assert "dashboard" in resp.location.lower()
        assert "tab=check-documents" in resp.location
