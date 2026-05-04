# Phase 2 Roadmap: Workspace-Based Submission Flow

## Current Objective
Continue expanding the working dashboard into a role workspace that keeps actions inside the page instead of redirecting to separate screens.

## Completed in This Phase
1. Authentication is already working for applicant and staff roles.
2. Dashboard tabs now behave like workspace buttons instead of navigation tabs.
3. Applicant submission is rendered inside the dashboard workspace.
4. OIDB document review is rendered inside the dashboard workspace.
5. One applicant can create one application with up to four optional PDF documents.

## Current Structure Goals
1. Keep the workspace style consistent across role sections.
2. Keep route handlers thin and move data shaping into models or helpers when appropriate.
3. Keep applicant submission read/write limited to the applicant role.
4. Keep OIDB document review read-only for now.

## Next Tasks
1. Add applicant edit and resubmit flow.
2. Add OIDB actions for marking an application as needing correction.
3. Add OIDB actions for approving and forwarding an application.
4. Add document download/view support with proper access control.
5. Expand remaining role tabs beyond their current placeholders.