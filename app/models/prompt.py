from sqlalchemy import Column, ForeignKey, Text, DateTime, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class Prompt(Base):
    __tablename__ = 'prompts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        'users.id'), nullable=False)
    original_prompt = Column(Text, nullable=False)
    optimized_prompt = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    total_tokens = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now())
    is_favorite = Column(Boolean, default=False)
