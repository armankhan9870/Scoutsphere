"""Resume upload, retrieval, and agent analysis endpoints."""

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.nodes.resume_analysis_node import run_resume_analysis_node
from app.agents.state import ScoutSphereState
from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.core.storage import StorageClient, get_storage_client
from app.models.resume import Resume
from app.models.user import User
from app.repositories.resume_repository import ResumeRepository
from app.schemas.ats_analysis import ATSAnalysisResponse
from app.schemas.resume import ResumeResponse, ResumeUploadResponse
from app.services.ats_analyzer import ATSAnalyzer
from app.services.pdf_parser import extract_text_from_pdf_bytes

router = APIRouter()


@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    storage: StorageClient = Depends(get_storage_client),
) -> ResumeUploadResponse:
    """Accepts a PDF/DOCX resume file upload, saves via StorageClient, and inserts Resume record into DB."""
    filename = file.filename or "resume.pdf"
    if not (filename.endswith(".pdf") or filename.endswith(".docx") or filename.endswith(".doc")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF (.pdf) and Word (.docx) files are supported.",
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    # Save to storage provider
    saved_path, file_id = await storage.save_file(file_bytes, filename)

    # Extract raw text from PDF
    extracted_text = extract_text_from_pdf_bytes(file_bytes)

    resume_repo = ResumeRepository(db)
    resume_uuid = uuid.UUID(file_id)

    # Deactivate older resumes
    await resume_repo.set_active(current_user.id, resume_uuid)

    # Create new active resume
    resume = Resume(
        id=resume_uuid,
        user_id=current_user.id,
        raw_text=extracted_text,
        file_path=saved_path,
        parsed_data_json={"filename": filename, "status": "UPLOADED"},
        is_active=True,
    )
    resume = await resume_repo.create(resume)

    return ResumeUploadResponse(
        id=resume.id,
        file_path=saved_path,
        is_active=True,
        created_at=resume.created_at,
    )


@router.get("/active", response_model=ResumeResponse)
async def get_active_resume(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Resume:
    """Fetches currently active resume for authenticated user."""
    repo = ResumeRepository(db)
    resume = await repo.get_active_by_user(current_user.id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active resume found for this user.",
        )
    return resume


@router.post("/{id}/analyze", response_model=ResumeResponse)
async def analyze_resume(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Resume:
    """Runs the Resume & Profile Analysis Agent on the target resume, normalizes skills, generates pgvector embedding, and persists results."""
    repo = ResumeRepository(db)
    resume = await repo.get_by_id(id)
    if not resume or resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )

    # Initial state
    initial_state: ScoutSphereState = {
        "user_id": str(current_user.id),
        "session_id": str(uuid.uuid4()),
        "current_intent": "analyze_resume",
        "raw_resume_text": resume.raw_text,
        "user_profile": {
            "target_roles": current_user.target_roles,
            "location_preference": current_user.location_preference,
        },
        "parsed_profile": None,
        "profile_embedding": None,
        "search_filters": None,
        "discovered_opportunities": None,
        "target_opportunity_id": None,
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

    # Execute LangGraph Resume Analysis Agent Node
    final_state = await run_resume_analysis_node(initial_state)

    parsed_profile = final_state.get("parsed_profile") or {}
    vector_embedding = final_state.get("profile_embedding")

    # Update database record
    updated_resume = await repo.update(
        id,
        parsed_data_json=parsed_profile,
        embedding=vector_embedding,
    )

    if not updated_resume:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist analysis results.",
        )

    return updated_resume


@router.post("/{id}/ats-analysis", response_model=ATSAnalysisResponse)
async def analyze_ats_resume(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ATSAnalysisResponse:
    """Executes standalone ATS Analysis evaluating parseability, section completeness, action verbs, metrics, keyword density, and length."""
    repo = ResumeRepository(db)
    resume = await repo.get_by_id(id)
    if not resume or resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )

    analyzer = ATSAnalyzer()
    ats_result = await analyzer.analyze(str(resume.id), resume.raw_text)

    # Persist ATS analysis result into resume's parsed_data_json under "ats_analysis" key
    parsed_json = dict(resume.parsed_data_json or {})
    parsed_json["ats_analysis"] = json_serializable_dict(ats_result.model_dump())
    await repo.update(id, parsed_data_json=parsed_json)
    await db.commit()

    return ats_result


def json_serializable_dict(d: dict) -> dict:
    """Recursively converts datetime and UUID objects to ISO strings for JSON storage."""
    result = {}
    for k, v in d.items():
        if isinstance(v, (uuid.UUID,)):
            result[k] = str(v)
        elif hasattr(v, "isoformat"):
            result[k] = v.isoformat()
        elif isinstance(v, dict):
            result[k] = json_serializable_dict(v)
        elif isinstance(v, list):
            result[k] = [
                (
                    json_serializable_dict(item)
                    if isinstance(item, dict)
                    else (
                        str(item)
                        if isinstance(item, uuid.UUID)
                        else (item.isoformat() if hasattr(item, "isoformat") else item)
                    )
                )
                for item in v
            ]
        else:
            result[k] = v
    return result
