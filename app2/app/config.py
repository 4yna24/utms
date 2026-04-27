"""Application constants and Phase 1 shell configuration."""

ROLE_DEFINITIONS = [
    {"name": "Applicant", "slug": "applicant"},
    {"name": "OIDB", "slug": "oidb"},
    {"name": "Dean", "slug": "dean"},
    {"name": "YGK", "slug": "ygk"},
    {"name": "YDYO", "slug": "ydyo"},
]

APPLICATION_SUBMISSION_PERIOD_OPEN = True
APPLICATION_REQUIRED_DOCUMENT_SLOTS = [1, 2, 3, 4]
APPLICATION_UPLOAD_SUBDIR = "uploads/applications"

PHASE1_TABS = {
    "applicant": [
        {
            "title": "Track Application",
            "description": "View transfer application status timeline.",
            "endpoint": "applicant_api.track_application",
            "period_open": True,
        },
        {
            "title": "Submit Documents",
            "description": "Upload and re-upload required files.",
            "endpoint": "applicant_api.submit_documents",
            "period_open": APPLICATION_SUBMISSION_PERIOD_OPEN,
        },
    ],
    "oidb": [
        {
            "title": "Check Documents",
            "description": "Placeholder queue for document checks.",
            "endpoint": "oidb_api.check_documents",
        },
        {
            "title": "Create Waitlist Table",
            "description": "Placeholder wizard for waitlist generation.",
            "endpoint": "oidb_api.create_waitlist_table",
        },
    ],
    "dean": [
        {
            "title": "Check Applicants",
            "description": "Placeholder controls for manual and auto forwarding.",
            "endpoint": "dean_api.check_applicants",
        },
    ],
    "ygk": [
        {
            "title": "Check Applicants",
            "description": "Placeholder list of applicants for evaluation.",
            "endpoint": "ygk_api.check_applicants",
        },
        {
            "title": "Intibak Table",
            "description": "Placeholder interface to view and edit intibak rows.",
            "endpoint": "ygk_api.intibak_table",
        },
    ],
    "ydyo": [
        {
            "title": "Retrieve Applicants",
            "description": "Placeholder retrieval queue.",
            "endpoint": "ydyo_api.retrieve_applicants",
        },
        {
            "title": "Set Prep School Status",
            "description": "Placeholder status assignment panel.",
            "endpoint": "ydyo_api.set_prep_school_status",
        },
    ],
}
