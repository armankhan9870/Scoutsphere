"""Tracking service managing state machine transitions, Kanban grouping, and pipeline analytics."""

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.models.application import Application

# Lifecycle state definitions
VALID_STATES = {
    "SAVED",
    "DRAFTING",
    "SUBMITTED",
    "APPLIED",
    "INTERVIEWING",
    "OFFER",
    "REJECTED",
    "WITHDRAWN",
}

# State transition matrix
ALLOWED_TRANSITIONS: Dict[str, List[str]] = {
    "SAVED": ["DRAFTING", "SUBMITTED", "APPLIED", "WITHDRAWN"],
    "DRAFTING": ["SUBMITTED", "APPLIED", "WITHDRAWN"],
    "SUBMITTED": ["INTERVIEWING", "REJECTED", "WITHDRAWN", "APPLIED"],
    "APPLIED": ["INTERVIEWING", "REJECTED", "WITHDRAWN"],
    "INTERVIEWING": ["OFFER", "REJECTED", "WITHDRAWN"],
    "OFFER": ["WITHDRAWN"],
    "REJECTED": [],
    "WITHDRAWN": [],
}


def is_valid_state_transition(current_status: str, new_status: str) -> bool:
    """Validates if moving from current_status to new_status is allowed."""
    curr = current_status.upper().strip()
    nxt = new_status.upper().strip()

    if curr not in VALID_STATES or nxt not in VALID_STATES:
        return False
    if curr == nxt:
        return True

    allowed = ALLOWED_TRANSITIONS.get(curr, [])
    return nxt in allowed


def group_applications_kanban(applications: List[Application]) -> Dict[str, List[Dict[str, Any]]]:
    """Groups application models into Kanban status columns."""
    kanban: Dict[str, List[Dict[str, Any]]] = {
        "SAVED": [],
        "DRAFTING": [],
        "APPLIED": [],
        "INTERVIEWING": [],
        "OFFER": [],
        "REJECTED": [],
        "WITHDRAWN": [],
    }

    for app in applications:
        status_key = app.status.upper()
        if status_key == "SUBMITTED":
            status_key = "APPLIED"

        bucket = kanban.get(status_key, kanban["SAVED"])
        opp = app.opportunity
        bucket.append(
            {
                "application_id": app.id,
                "opportunity_id": app.opportunity_id,
                "opportunity_title": opp.title if opp else "Opportunity",
                "company_name": opp.company_name if opp else "Company",
                "status": app.status,
                "cover_letter_preview": (
                    (app.cover_letter[:120] + "...") if app.cover_letter else None
                ),
                "updated_at": app.updated_at,
            }
        )

    return kanban


def calculate_pipeline_stats(applications: List[Application]) -> Dict[str, Any]:
    """Calculates application status counts, response rate %, and stale nudges."""
    counts = {
        "total": len(applications),
        "SAVED": 0,
        "DRAFTING": 0,
        "APPLIED": 0,
        "INTERVIEWING": 0,
        "OFFER": 0,
        "REJECTED": 0,
        "WITHDRAWN": 0,
    }

    now = datetime.now(timezone.utc)
    stale_nudge_list = []
    upcoming_deadlines = []

    for app in applications:
        st = app.status.upper()
        if st == "SUBMITTED":
            st = "APPLIED"
        if st in counts:
            counts[st] += 1

        # Check stale applied applications (no update in >= 14 days)
        if st in ("APPLIED", "SUBMITTED") and app.updated_at:
            days_since_update = (now - app.updated_at).days
            if days_since_update >= 14:
                stale_nudge_list.append(
                    {
                        "application_id": app.id,
                        "company_name": (
                            app.opportunity.company_name if app.opportunity else "Company"
                        ),
                        "opportunity_title": app.opportunity.title if app.opportunity else "Role",
                        "days_inactive": days_since_update,
                        "nudge_message": f"Applied {days_since_update} days ago. Consider sending a polite follow-up email.",
                    }
                )

        # Check deadline proximity (deadline within next 7 days)
        if app.opportunity and app.opportunity.deadline:
            days_to_deadline = (app.opportunity.deadline - now).days
            if 0 <= days_to_deadline <= 7:
                upcoming_deadlines.append(
                    {
                        "opportunity_id": app.opportunity.id,
                        "title": app.opportunity.title,
                        "company_name": app.opportunity.company_name,
                        "days_remaining": days_to_deadline,
                    }
                )

    # Response Rate Calculation: (Interviewing + Offer + Rejected) / (Applied + Interviewing + Offer + Rejected)
    evaluated = counts["APPLIED"] + counts["INTERVIEWING"] + counts["OFFER"] + counts["REJECTED"]
    responded = counts["INTERVIEWING"] + counts["OFFER"] + counts["REJECTED"]
    response_rate = round((responded / evaluated * 100.0), 1) if evaluated > 0 else 0.0

    return {
        "total_applications": counts["total"],
        "counts_by_status": counts,
        "response_rate_percentage": response_rate,
        "stale_followup_nudges": stale_nudge_list,
        "upcoming_deadlines": upcoming_deadlines,
    }
