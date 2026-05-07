"""Application constants and Phase 1 shell configuration."""

ROLE_DEFINITIONS = [
    {"name": "Applicant", "slug": "applicant"},
    {"name": "OIDB", "slug": "oidb"},
    {"name": "Dean", "slug": "dean"},
    {"name": "YGK", "slug": "ygk"},
    {"name": "YDYO", "slug": "ydyo"},
]

APPLICATION_SUBMISSION_PERIOD_OPEN = True
APPLICATION_CANCELLATION_ALLOWED = True
APPLICATION_RESUBMISSION_ALLOWED = True
APPLICATION_UPLOAD_SUBDIR = "uploads/applications"

APPLICATION_DOCUMENT_SLOTS = [
    {"slot": 1, "label": "Student Certificate"},
    {"slot": 2, "label": "Transcript"},
    {"slot": 3, "label": "YKS Score Report"},
    {"slot": 4, "label": "English Proficiency Certificate", "optional": True},
]
# Legacy alias — only required slots
APPLICATION_REQUIRED_DOCUMENT_SLOTS = [s["slot"] for s in APPLICATION_DOCUMENT_SLOTS if not s.get("optional")]

AVAILABLE_PROGRAMS = [
    "Computer Engineering",
    "Electrical and Electronics Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Industrial Engineering",
    "Software Engineering",
    "Architecture",
    "Business Administration",
    "Economics",
    "International Relations",
    "Psychology",
    "Law",
    "Medicine",
    "Nursing",
    "Mathematics",
    "Physics",
    "Chemistry",
    "Biology",
]

AVAILABLE_SEMESTERS = [
    "2024–2025 / Fall",
    "2024–2025 / Spring",
    "2025–2026 / Fall",
    "2025–2026 / Spring",
]

# Ordered steps for the applicant status tracker
APPLICATION_TRACKER_STEPS = [
    "Application Submitted",
    "Initial Verification",
    "Forwarding to Dean's Office",
    "Under Departmental Review",
    "Intibak Process",
    "Result Announcement",
]

# Maps application.status → tracker step index (0-based)
APPLICATION_STATUS_STEP = {
    "submitted": 0,
    "returned": 0,       # error at step 0
    "forwarded_to_ydyo": 2,
    "cancelled": -1,
}

PHASE1_TABS = {
    "applicant": [
        {
            "title": "Track Application",
            "description": "View your transfer application status and timeline.",
            "endpoint": "applicant_api.track_application",
            "period_open": True,
            "partial": "partials/panel_applicant_track.html",
        },
        {
            "title": "Submit Application",
            "description": "Submit required documents and personal information.",
            "endpoint": "applicant_api.submit_documents",
            "period_open": APPLICATION_SUBMISSION_PERIOD_OPEN,
            "partial": "partials/panel_applicant_submit.html",
        },
    ],
    "oidb": [
        {
            "title": "Check Documents",
            "description": "Review submitted applications and verify documents.",
            "endpoint": "oidb_api.check_documents",
            "partial": "partials/panel_oidb_documents.html",
        },
        {
            "title": "Create Waitlist Table",
            "description": "Placeholder wizard for waitlist generation.",
            "endpoint": "oidb_api.create_waitlist_table",
            "partial": None,
        },
    ],
    "dean": [
        {
            "title": "Receive & Forward Applications",
            "description": "Review and forward applications to YGK.",
            "endpoint": "dean_api.check_applicants",
            "partial": "partials/panel_dean_applications.html",
        },
    ],
    "ygk": [
        {
            "title": "Check Applicants",
            "description": "Applicant list for evaluation.",
            "endpoint": "ygk_api.check_applicants",
            "partial": None,
        },
        {
            "title": "Intibak Table",
            "description": "View and edit intibak rows.",
            "endpoint": "ygk_api.intibak_table",
            "partial": None,
        },
    ],
    "ydyo": [
        {
            "title": "Retrieve Applicants",
            "description": "Retrieval queue.",
            "endpoint": "ydyo_api.retrieve_applicants",
            "partial": None,
        },
        {
            "title": "Set Prep School Status",
            "description": "Status assignment panel.",
            "endpoint": "ydyo_api.set_prep_school_status",
            "partial": None,
        },
    ],
}
