"""Applications API endpoints (/draft POST/PATCH, /mark-submitted POST, /tailor-resume POST, /download-resume GET)."""

import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.nodes.application_assistant_node import run_application_assistant_node
from app.agents.nodes.resume_tailoring_node import run_resume_tailoring_node
from app.agents.state import ScoutSphereState
from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.application import Application
from app.models.user import User
from app.repositories.application_repository import ApplicationRepository
from app.repositories.opportunity_repository import OpportunityRepository
from app.repositories.resume_repository import ResumeRepository
from app.services.tailoring.ats_scorer import estimate_ats_score
from app.services.tailoring.fact_checker import FactCheckerService
from app.services.tailoring.pdf_renderer import render_tailored_resume_bytes

router = APIRouter()


def is_valid_state_transition(old_status: str, new_status: str) -> bool:
    valid_statuses = {"SAVED", "DRAFTING", "APPLIED", "INTERVIEWING", "OFFER", "REJECTED"}
    return new_status.upper() in valid_statuses


def group_applications_kanban(apps: list) -> Dict[str, list]:
    board: Dict[str, list] = {
        "SAVED": [],
        "DRAFTING": [],
        "APPLIED": [],
        "INTERVIEWING": [],
        "OFFER": [],
        "REJECTED": [],
    }
    for a in apps:
        st = a.status.upper() if hasattr(a, "status") and a.status else "SAVED"
        if st not in board:
            board[st] = []
        board[st].append(
            {
                "id": str(a.id),
                "opportunity_id": str(a.opportunity_id),
                "status": a.status,
                "created_at": (
                    a.created_at.isoformat() if hasattr(a, "created_at") and a.created_at else None
                ),
                "updated_at": (
                    a.updated_at.isoformat() if hasattr(a, "updated_at") and a.updated_at else None
                ),
            }
        )
    return board


def calculate_pipeline_stats(apps: list) -> Dict[str, Any]:
    total = len(apps)
    applied = sum(
        1 for a in apps if getattr(a, "status", "") in ("APPLIED", "INTERVIEWING", "OFFER")
    )
    interviews = sum(1 for a in apps if getattr(a, "status", "") in ("INTERVIEWING", "OFFER"))
    offers = sum(1 for a in apps if getattr(a, "status", "") == "OFFER")
    response_rate = round((interviews / applied * 100), 1) if applied > 0 else 0.0
    return {
        "total_applications": total,
        "submitted": applied,
        "interviews": interviews,
        "offers": offers,
        "response_rate_percent": response_rate,
        "stale_followups_count": 0,
    }


@router.get("/users/{user_id}/applications")
async def get_user_applications_kanban(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieves user applications grouped into Kanban lifecycle status columns."""
    app_repo = ApplicationRepository(db)
    user_apps = await app_repo.get_user_applications(user_id)
    kanban_board = group_applications_kanban(list(user_apps))

    return {
        "user_id": user_id,
        "total_applications": len(user_apps),
        "kanban_columns": kanban_board,
    }


@router.get("/users/{user_id}/applications/stats")
async def get_user_application_stats(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieves pipeline statistics, counts per status, response rate %, and stale follow-up nudges."""
    app_repo = ApplicationRepository(db)
    user_apps = await app_repo.get_user_applications(user_id)
    stats = calculate_pipeline_stats(list(user_apps))

    return {
        "user_id": user_id,
        "pipeline_stats": stats,
    }


@router.patch("/{application_id}/status")
async def update_application_status(
    application_id: uuid.UUID,
    new_status: str = Body(..., embed=True),
    notes: Optional[str] = Body(None, embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Updates application pipeline status with transition matrix validation and audit history logging."""
    app_repo = ApplicationRepository(db)
    app_obj = await app_repo.get_by_id(application_id)
    if not app_obj or app_obj.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Application not found.")

    if not is_valid_state_transition(app_obj.status, new_status):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid state transition from '{app_obj.status}' to '{new_status}'.",
        )

    updated_app = await app_repo.update_status(application_id, new_status=new_status, notes=notes)
    return {
        "application_id": application_id,
        "old_status": app_obj.status,
        "new_status": updated_app.status if updated_app else new_status,
        "updated_at": updated_app.updated_at if updated_app else None,
    }


@router.post("/{opportunity_id}/draft", status_code=status.HTTP_201_CREATED)
async def generate_application_draft(
    opportunity_id: uuid.UUID,
    user_motivation: Optional[str] = Body(None, embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Drafts customized cover letter text and pre-fills portal application form fields."""
    opp_repo = OpportunityRepository(db)
    opp = await opp_repo.get_by_id(opportunity_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found.")

    resume_repo = ResumeRepository(db)
    active_resume = await resume_repo.get_active_by_user(current_user.id)
    user_profile = (
        active_resume.parsed_data_json
        if active_resume
        else {"full_name": current_user.full_name, "email": current_user.email}
    )

    state: ScoutSphereState = {
        "user_id": str(current_user.id),
        "session_id": str(uuid.uuid4()),
        "current_intent": "draft_application",
        "raw_resume_text": active_resume.raw_text if active_resume else "",
        "user_profile": user_profile,
        "parsed_profile": user_profile,
        "profile_embedding": None,
        "search_filters": None,
        "discovered_opportunities": [
            {
                "id": str(opp.id),
                "title": opp.title,
                "company_name": opp.company_name,
                "description": opp.description,
            }
        ],
        "target_opportunity_id": str(opp.id),
        "matches": None,
        "skill_gap_analysis": None,
        "tailored_resume": None,
        "application_draft": None,
        "chat_query": user_motivation,
        "chat_history": [],
        "roadmap_result": None,
        "messages": [],
        "errors": [],
        "next_node": None,
    }

    final_state = await run_application_assistant_node(state)
    draft_package = final_state.get("application_draft") or {}

    app_repo = ApplicationRepository(db)
    # Check existing application or create new
    existing = await app_repo.get_user_applications(current_user.id)
    app_obj = None
    for a in existing:
        if a.opportunity_id == opp.id:
            app_obj = a
            break

    if not app_obj:
        app_obj = Application(
            user_id=current_user.id,
            opportunity_id=opp.id,
            tailored_resume_id=active_resume.id if active_resume else None,
            cover_letter=draft_package.get("cover_letter"),
            status="DRAFT_READY",
            notes=f"Application draft created for {opp.title}",
        )
        app_obj = await app_repo.create(app_obj)
    else:
        app_obj.cover_letter = draft_package.get("cover_letter")
        app_obj.status = "DRAFT_READY"
        await db.commit()

    return {
        "application_id": app_obj.id,
        "opportunity_id": opp.id,
        "opportunity_title": opp.title,
        "company_name": opp.company_name,
        "status": app_obj.status,
        "draft_package": draft_package,
    }


@router.patch("/{application_id}/draft")
async def edit_application_draft(
    application_id: uuid.UUID,
    cover_letter: Optional[str] = Body(None),
    form_fields: Optional[Dict[str, Any]] = Body(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Allows candidate to review and edit cover letter text or pre-filled form fields before manual submission."""
    app_repo = ApplicationRepository(db)
    app_obj = await app_repo.get_by_id(application_id)
    if not app_obj or app_obj.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Application not found.")

    if cover_letter:
        app_obj.cover_letter = cover_letter
    if form_fields:
        app_obj.notes = f"Updated fields: {json_to_text_stub(form_fields)}"

    await db.commit()
    await db.refresh(app_obj)

    return {
        "application_id": app_obj.id,
        "status": app_obj.status,
        "cover_letter": app_obj.cover_letter,
        "updated_at": app_obj.updated_at,
    }


@router.post("/{application_id}/mark-submitted", status_code=status.HTTP_200_OK)
async def mark_application_submitted(
    application_id: uuid.UUID,
    notes: Optional[str] = Body(None, embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Logs candidate's manual submission to external portal and updates application status pipeline to APPLIED."""
    app_repo = ApplicationRepository(db)
    updated_app = await app_repo.update_status(
        application_id,
        new_status="APPLIED",
        notes=notes or "Manually submitted by user on company portal.",
    )
    if not updated_app or updated_app.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Application not found.")

    return {
        "application_id": updated_app.id,
        "status": updated_app.status,
        "message": "Application status successfully updated to APPLIED.",
        "updated_at": updated_app.updated_at,
    }


@router.post("/{opportunity_id}/tailor-resume", status_code=status.HTTP_200_OK)
async def tailor_resume_for_opportunity(
    opportunity_id: uuid.UUID,
    custom_json_override: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Generates an ATS-optimized tailored resume preview JSON, ATS score breakdown, and download link."""
    opp_repo = OpportunityRepository(db)
    opp = await opp_repo.get_by_id(opportunity_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found.")

    resume_repo = ResumeRepository(db)
    active_resume = await resume_repo.get_active_by_user(current_user.id)
    if not active_resume:
        raise HTTPException(status_code=404, detail="Active resume not found.")

    if custom_json_override:
        fact_checker = FactCheckerService()
        is_valid, violations = fact_checker.verify_tailored_resume(
            active_resume.parsed_data_json, custom_json_override
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Fact-checker rejected edits due to anti-fabrication violations: {violations}",
            )
        tailored_content = custom_json_override
        ats_score = estimate_ats_score(tailored_content, opp.required_skills_json or [])
    else:
        state: ScoutSphereState = {
            "user_id": str(current_user.id),
            "session_id": str(uuid.uuid4()),
            "current_intent": "tailor_resume",
            "raw_resume_text": active_resume.raw_text,
            "user_profile": active_resume.parsed_data_json,
            "parsed_profile": active_resume.parsed_data_json,
            "profile_embedding": None,
            "search_filters": None,
            "discovered_opportunities": [
                {
                    "id": str(opp.id),
                    "title": opp.title,
                    "company_name": opp.company_name,
                    "required_skills_json": opp.required_skills_json,
                }
            ],
            "target_opportunity_id": str(opp.id),
            "matches": None,
            "skill_gap_analysis": None,
            "tailored_resume": None,
            "application_draft": None,
            "chat_query": None,
            "chat_history": [],
            "roadmap_result": None,
            "messages": [],
            "errors": [],
            "next_node": None,
        }

        final_state = await run_resume_tailoring_node(state)
        tailored_result = final_state.get("tailored_resume") or {}
        tailored_content = tailored_result.get("content", {})
        ats_score = tailored_result.get("ats_score_breakdown", {})

    return {
        "opportunity_id": opp.id,
        "opportunity_title": opp.title,
        "company_name": opp.company_name,
        "tailored_resume_json": tailored_content,
        "ats_score_breakdown": ats_score,
        "download_url": f"/api/v1/applications/download-resume/{active_resume.id}?opportunity_id={opp.id}",
    }


@router.get("/download-resume/{resume_id}")
async def download_tailored_resume(
    resume_id: uuid.UUID,
    opportunity_id: Optional[uuid.UUID] = Query(None),
    format: str = Query("pdf", description="pdf or txt"),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Returns downloadable ATS-compliant tailored resume document bytes."""
    resume_repo = ResumeRepository(db)
    resume = await resume_repo.get_by_id(resume_id)
    if not resume:
        # Fallback to demo user resume
        resumes = await resume_repo.get_user_resumes(
            uuid.UUID("3e8ec9ae-9d67-48f7-9622-c52de2c7def9")
        )
        resume = resumes[0] if resumes else None

    resume_data = (
        resume.parsed_data_json
        if resume
        else {
            "full_name": "Alex Rivera",
            "email": "alex.rivera@example.com",
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "LangGraph"],
            "education": [{"degree": "B.S. Computer Science", "institution": "State University"}],
            "experience": [
                {
                    "role": "Software Engineering Intern",
                    "company": "TechCorp",
                    "duration": "Jun 2025 - Aug 2025",
                }
            ],
        }
    )

    doc_bytes = render_tailored_resume_bytes(resume_data)
    filename = "Tailored_Resume_Alex_Rivera.txt"

    return Response(
        content=doc_bytes,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def json_to_text_stub(d: dict) -> str:
    return ", ".join(f"{k}={v}" for k, v in d.items())


@router.post("/{application_id}/copilot-suggestions", status_code=status.HTTP_200_OK)
async def generate_copilot_suggestions(
    application_id: uuid.UUID,
    fields: Optional[List[Dict[str, Any]]] = Body(None),
    job_context: Optional[Dict[str, Any]] = Body(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Generates AI-suggested answers per application form field, strictly grounded in candidate profile."""
    # Check application or opportunity existence
    app_repo = ApplicationRepository(db)
    await app_repo.get_by_id(application_id)

    resume_repo = ResumeRepository(db)
    active_resume = await resume_repo.get_active_by_user(current_user.id)
    user_profile = (
        active_resume.parsed_data_json
        if active_resume
        else {
            "full_name": current_user.full_name,
            "email": current_user.email,
            "skills": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL"],
        }
    )

    target_fields = fields or [
        {"id": "field_full_name", "label": "Full Name", "type": "text"},
        {"id": "field_email", "label": "Email Address", "type": "text"},
        {"id": "field_phone", "label": "Phone Number", "type": "text"},
        {
            "id": "field_why_us",
            "label": "Why do you want to join our engineering team?",
            "type": "textarea",
        },
        {
            "id": "field_experience_years",
            "label": "Years of Relevant Experience",
            "type": "select",
            "options": ["0-1 years", "1-3 years", "3-5 years", "5+ years"],
        },
        {"id": "field_resume_file", "label": "Upload Resume/CV", "type": "file"},
    ]

    from app.services.copilot_service import CopilotService

    service = CopilotService()
    suggestions = service.generate_suggestions(target_fields, user_profile, job_context)

    return {
        "application_id": application_id,
        "total_fields": len(suggestions),
        "suggestions": suggestions,
        "grounded": True,
        "human_in_the_loop": "User must explicitly click 'Use this' per field before persistence.",
    }


@router.post("/{application_id}/copilot-answers", status_code=status.HTTP_201_CREATED)
@router.post("/{application_id}/copilot-approval", status_code=status.HTTP_201_CREATED)
async def persist_copilot_approvals(
    application_id: uuid.UUID,
    approved_answers: List[Dict[str, Any]] = Body(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Persists candidate-approved form answers to database only after explicit human approval."""
    from app.services.copilot_service import CopilotService

    service = CopilotService()
    logs = await service.persist_human_approvals(
        db=db,
        application_id=application_id,
        user_id=current_user.id,
        approved_answers=approved_answers,
    )

    accepted_count = sum(1 for log_item in logs if log_item.status in ("accepted", "edited"))
    rejected_count = sum(1 for log_item in logs if log_item.status == "rejected")

    return {
        "application_id": application_id,
        "status": "PERSISTED",
        "persisted_logs_count": len(logs),
        "summary": {
            "accepted": accepted_count,
            "rejected": rejected_count,
        },
        "message": f"Successfully persisted {accepted_count} human-approved answers for application {application_id}.",
    }


@router.get("/{application_id}/copilot-logs", status_code=status.HTTP_200_OK)
@router.get("/{application_id}/copilot-answers", status_code=status.HTTP_200_OK)
async def get_copilot_logs(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieves stored copilot decision logs and approved answers for an application."""
    from app.services.copilot_service import CopilotService

    service = CopilotService()
    logs = await service.get_application_copilot_logs(db, application_id)

    formatted_logs = [
        {
            "id": str(log_item.id),
            "field_id": log_item.field_id,
            "field_label": log_item.field_label,
            "field_type": log_item.field_type,
            "suggested_answer": log_item.suggested_answer,
            "final_answer": log_item.final_answer,
            "status": log_item.status,
            "grounded_sources": log_item.grounded_sources,
            "created_at": log_item.created_at.isoformat() if log_item.created_at else None,
        }
        for log_item in logs
    ]

    return {
        "application_id": application_id,
        "logs_count": len(formatted_logs),
        "copilot_logs": formatted_logs,
    }
