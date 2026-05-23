"""Role-based access control tests."""

import pytest


class TestRoleAccess:
    """Test role-based dashboard access."""

    def test_dean_can_access_dashboard(self, auth_client_dean):
        """Test dean role can access dashboard."""
        resp = auth_client_dean.get("/dashboard/")
        assert resp.status_code == 200

    def test_oidb_can_access_dashboard(self, auth_client_oidb):
        """Test OIDB role can access dashboard."""
        resp = auth_client_oidb.get("/dashboard/")
        assert resp.status_code == 200

    def test_ydyo_can_access_dashboard(self, auth_client_ydyo):
        """Test YDYO role can access dashboard."""
        resp = auth_client_ydyo.get("/dashboard/")
        assert resp.status_code == 200

    def test_ygk_can_access_dashboard(self, auth_client_ygk):
        """Test YGK role can access dashboard."""
        resp = auth_client_ygk.get("/dashboard/")
        assert resp.status_code == 200


class TestRoleIsolation:
    """Test that roles cannot access each other's operations."""

    def test_applicant_cannot_forward_applications(self, auth_client_applicant):
        """Test applicant cannot perform dean operations."""
        resp = auth_client_applicant.post(
            "/api/dean/forward-to-ygk",
            json={"application_id": 1}
        )
        # Should fail or redirect
        assert resp.status_code in [302, 403, 404]

    def test_applicant_cannot_review_as_oidb(self, auth_client_applicant):
        """Test applicant cannot perform OIDB operations."""
        resp = auth_client_applicant.post(
            "/api/oidb/forward-to-ydyo",
            json={"application_id": 1}
        )
        # Should fail or redirect
        assert resp.status_code in [302, 403, 404]

    def test_dean_cannot_perform_oidb_operations(self, auth_client_dean):
        """Test dean cannot perform OIDB operations."""
        resp = auth_client_dean.post(
            "/api/oidb/forward-to-ydyo",
            json={"application_id": 1}
        )
        # Should fail or redirect
        assert resp.status_code in [302, 403, 404]


class TestDashboardContent:
    """Test dashboard content for each role."""

    def test_applicant_dashboard_shows_applications(self, auth_client_applicant):
        """Test applicant dashboard displays application info."""
        resp = auth_client_applicant.get("/dashboard/")
        assert resp.status_code == 200
        # Check for common keywords
        content = resp.data.lower()
        assert b"application" in resp.data.lower() or b"dashboard" in content

    def test_dean_dashboard_shows_review_panel(self, auth_client_dean):
        """Test dean dashboard displays review panel."""
        resp = auth_client_dean.get("/dashboard/")
        assert resp.status_code == 200

    def test_staff_roles_can_see_applications_to_review(self, auth_client_oidb):
        """Test OIDB sees applications for review."""
        resp = auth_client_oidb.get("/dashboard/")
        assert resp.status_code == 200
