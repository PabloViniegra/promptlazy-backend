from fastapi import APIRouter, HTTPException, Depends
from fastapi import Query
from sqlalchemy.orm import Session
from app.schemas.prompt import PromptRequest, PromptResponse
from app.services.prompt_service import improve_prompt
from app.api.auth import get_current_user
from app.models.user import User
from app.db.session import SessionLocal
from uuid import UUID
from app.schemas.prompt import PromptListResponse, PromptRequest
from app.services.prompt_service import (
    list_prompts, get_prompt_by_id, regenerate_prompt, delete_prompt,
    toggle_favorite_prompt, list_favorite_prompts
)

router = APIRouter(prefix="/prompt", tags=["Prompt"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=PromptListResponse)
def list_user_prompts(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns a list of all prompts created by the authenticated user.
    """
    prompts = list_prompts(db, user)
    return {"prompts": prompts}


@router.get("/favorites", response_model=PromptListResponse)
def get_favorites(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns a list of all favorite prompts for the authenticated user.
    """
    prompts = list_favorite_prompts(db, user)
    return {"prompts": prompts}


@router.get("/{prompt_id}", response_model=PromptResponse)
def get_prompt(prompt_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Retrieves a specific prompt by its ID for the authenticated user.
    """
    return get_prompt_by_id(db, user, prompt_id)


@router.put("/{prompt_id}", response_model=PromptResponse)
def regenerate(prompt_id: UUID, body: PromptRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Regenerates an optimized prompt and explanation for a given prompt ID using new text.
    """
    return regenerate_prompt(db, user, prompt_id, body.prompt)


@router.delete("/{prompt_id}", status_code=204)
def delete(prompt_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Deletes a prompt by its ID for the authenticated user.
    """
    delete_prompt(db, user, prompt_id)
    return


@router.post("/improve", response_model=PromptResponse)
def improve(prompt: PromptRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Improves a given prompt using AI and returns the optimized prompt and explanation.
    Raises HTTPException if the prompt is empty.
    """
    if not prompt.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    return improve_prompt(user, prompt.prompt, db)


@router.patch("/{prompt_id}/favorite", response_model=PromptResponse)
def toggle_favorite(prompt_id: UUID, favorite: bool = Query(True), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Sets or unsets a prompt as favorite for the authenticated user.
    Returns the updated prompt.
    """
    return toggle_favorite_prompt(db, user, prompt_id, favorite)
