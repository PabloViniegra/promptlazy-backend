from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class PromptRequest(BaseModel):
    prompt: str


class PromptResponse(BaseModel):
    id: UUID
    original_prompt: str
    optimized_prompt: str
    explanation: Optional[str] = None
    total_tokens: int
    created_at: datetime
    is_favorite: bool


class PromptListResponse(BaseModel):
    prompts: List[PromptResponse]
