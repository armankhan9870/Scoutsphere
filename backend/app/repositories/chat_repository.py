"""ChatRepository for chat session management and message history retrieval."""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat import ChatMessage, ChatSession
from app.repositories.base import BaseRepository


class ChatRepository(BaseRepository[ChatSession]):
    """Data access repository for ChatSession entities."""

    def __init__(self, db: AsyncSession):
        super().__init__(ChatSession, db)

    async def get_session_with_messages(self, session_id: uuid.UUID) -> Optional[ChatSession]:
        """Fetch a chat session with all messages ordered by creation time."""
        result = await self.db.execute(
            select(ChatSession)
            .options(selectinload(ChatSession.messages))
            .where(ChatSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def add_message(
        self,
        session_id: uuid.UUID,
        sender_role: str,
        content: str,
        context_metadata: Optional[dict] = None,
    ) -> ChatMessage:
        """Appends a new message to a chat session thread."""
        message = ChatMessage(
            session_id=session_id,
            sender_role=sender_role,
            content=content,
            context_metadata_json=context_metadata or {},
        )
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message
