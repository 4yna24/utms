"""Applicant workflow and access tests."""

import pytest


class TestApplicantAccess:
    def test_dashboard_blocked_unauthenticated(self, client):
        resp = client.get("/dashboard/", follow_redirects=False)
        assert resp.status_code == 302
        assert "login" in resp.location.lower() or "auth" in resp.location.lower()

    def test_dashboard_accessible(self, auth_client_applicant):
        assert auth_client_applicant.get("/dashboard/").status_code == 200

    def test_submit_documents_page_get(self, auth_client_applicant):
        resp = auth_client_applicant.get("/api/applicant/submit-documents")
        assert resp.status_code == 200

    def test_track_application_endpoint(self, auth_client_applicant):
        resp = auth_client_applicant.get("/api/applicant/track-application")
        assert resp.status_code == 200

    def test_applicant_cannot_access_oidb_check(self, auth_client_applicant):
        resp = auth_client_applicant.get("/api/oidb/check-documents", follow_redirects=False)
        assert resp.status_code == 302

    def test_applicant_cannot_access_dean_check(self, auth_client_applicant):
        resp = auth_client_applicant.get("/api/dean/check-applicants", follow_redirects=False)
        assert resp.status_code == 302


class TestApplicantTabContent:
    def test_track_tab_loads(self, auth_client_applicant):
        resp = auth_client_applicant.get("/dashboard/tab/track-application")
        assert resp.status_code == 200
        assert b"application" in resp.data.lower() or b"submit" in resp.data.lower()

    def test_submit_tab_loads(self, auth_client_applicant):
        resp = auth_client_applicant.get("/dashboard/tab/submit-application")
        assert resp.status_code == 200

    def test_track_tab_with_application(self, auth_client_applicant, application_submitted):
        resp = auth_client_applicant.get("/dashboard/tab/track-application")
        assert resp.status_code == 200
        assert b"submitted" in resp.data.lower() or b"application" in resp.data.lower()


class TestApplicantSubmission:
    def test_submit_redirects_unauthenticated(self, client):
        resp = client.post("/api/applicant/submit-documents", follow_redirects=False)
        assert resp.status_code == 302

    def test_cancel_redirects_unauthenticated(self, client):
        resp = client.post("/api/applicant/cancel-application", follow_redirects=False)
        assert resp.status_code == 302

    def test_cancel_when_no_application(self, auth_client_applicant):
        resp = auth_client_applicant.post(
            "/api/applicant/cancel-application",
            follow_redirects=False,
        )
        assert resp.status_code == 302

    def test_resubmit_requires_returned_status(self, auth_client_applicant, application_submitted):
        # application_submitted has status="submitted", not "returned" — should be rejected
        resp = auth_client_applicant.post(
            "/api/applicant/resubmit-application",
            follow_redirects=False,
        )
        assert resp.status_code == 302
