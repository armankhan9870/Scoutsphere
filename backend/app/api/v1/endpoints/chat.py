"""Chat API endpoints (/chat/sessions POST, /chat/sessions/{id}/messages POST)."""

import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.nodes.chat_node import run_chat_agent_node
from app.agents.state import ScoutSphereState
from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.chat import ChatSession
from app.models.user import User
from app.repositories.chat_repository import ChatRepository
from app.repositories.resume_repository import ResumeRepository
from app.services.rag.rag_retriever import RAGRetriever

router = APIRouter()


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    title: Optional[str] = Body(None, embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Creates a new conversational chat session for authenticated user."""
    repo = ChatRepository(db)
    session = ChatSession(
        user_id=current_user.id,
        title=title or "Career Guidance Conversation",
        session_type="GENERAL",
    )
    session = await repo.create(session)

    # Initial greeting message
    greeting = await repo.add_message(
        session_id=session.id,
        sender_role="assistant",
        content=f"Hello {current_user.full_name}! I am your ScoutSphere Career AI Assistant. How can I help with your job search, skill gaps, or career roadmaps today?",
    )

    return {
        "session_id": session.id,
        "title": session.title,
        "created_at": session.created_at,
        "initial_message": greeting.content,
    }


@router.post("/sessions/{session_id}/messages")
async def send_chat_message(
    session_id: uuid.UUID,
    content: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Sends a student message to the RAG Career Chatbot and returns grounded assistant response."""
    chat_repo = ChatRepository(db)
    session = await chat_repo.get_by_id(session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    # Record user message
    user_msg = await chat_repo.add_message(
        session_id=session.id,
        sender_role="user",
        content=content,
    )

    # RAG Retrieval
    retriever = RAGRetriever(db)
    rag_context = await retriever.get_user_rag_context(current_user.id, query=content)

    resume_repo = ResumeRepository(db)
    active_resume = await resume_repo.get_active_by_user(current_user.id)
    user_profile = (
        active_resume.parsed_data_json if active_resume else {"full_name": current_user.full_name}
    )

    state: ScoutSphereState = {
        "user_id": str(current_user.id),
        "session_id": str(session_id),
        "current_intent": "chat",
        "raw_resume_text": active_resume.raw_text if active_resume else "",
        "user_profile": user_profile,
        "parsed_profile": user_profile,
        "profile_embedding": None,
        "search_filters": None,
        "discovered_opportunities": None,
        "target_opportunity_id": None,
        "matches": None,
        "skill_gap_analysis": None,
        "tailored_resume": None,
        "application_draft": None,
        "chat_query": content,
        "chat_history": [],
        "rag_context": rag_context,
        "roadmap_result": None,
        "messages": [],
        "errors": [],
        "next_node": None,
    }

    final_state = await run_chat_agent_node(state)
    chat_history = final_state.get("chat_history") or []
    assistant_reply = (
        chat_history[-1]["content"]
        if chat_history
        else "I can help guide your career path based on your resume and skill profile."
    )

    # Record assistant message
    assistant_msg = await chat_repo.add_message(
        session_id=session.id,
        sender_role="assistant",
        content=assistant_reply,
        context_metadata={"grounded_context_retrieved": True},
    )

    return {
        "session_id": session.id,
        "user_message_id": user_msg.id,
        "assistant_message_id": assistant_msg.id,
        "reply": assistant_reply,
        "created_at": assistant_msg.created_at,
    }
