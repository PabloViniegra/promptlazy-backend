from app.core.security import openai
from app.models.prompt import Prompt
from sqlalchemy.orm import Session
from app.models.user import User
from openai import OpenAIError
from uuid import UUID
from fastapi import HTTPException

system_prompt = """
Eres un experto en prompt engineering. Tu tarea es mejorar el siguiente prompt para que sea más claro, detallado y efectivo. Si es posible, agrega contexto y estructura, formato de salida deseado y contexto adicional. Luego explica brevemente los cambios realizados. La idea es optimizar el prompt para que sea más útil y preciso para el modelo de IA.
"""


def improve_prompt(user: User, prompt_text: str, db: Session) -> Prompt:
    """
    Improves a given prompt using OpenAI's GPT-4 model.
    Returns a Prompt object with the optimized prompt and an explanation of the changes.
    Raises an exception if the OpenAI API fails.
    """
    try:
        response = openai.chat.completions.create(
            model='gpt-4',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_text}
            ]
        )
    except OpenAIError as e:
        raise Exception(f"OpenAI API error: {str(e)}")

    content = response.choices[0].message.content
    total_tokens = response.usage.total_tokens

    optimized = content.strip()
    explanation = None

    if "\n\nExplicación:" in content:
        try:
            optimized, explanation = content.split("\n\nExplicación:", 1)
            optimized = optimized.strip()
            explanation = explanation.strip()
        except ValueError:
            pass

    prompt = Prompt(
        user_id=user.id,
        original_prompt=prompt_text,
        optimized_prompt=optimized.strip(),
        explanation=explanation.strip() if explanation else None,
        total_tokens=total_tokens,
    )
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt


def list_prompts(db: Session, user: User) -> list[Prompt]:
    """
    Returns a list of all prompts created by the user, ordered by creation date (descending).
    """
    return db.query(Prompt).filter(Prompt.user_id == user.id).order_by(Prompt.created_at.desc()).all()


def get_prompt_by_id(db: Session, user: User, prompt_id: UUID) -> Prompt:
    """
    Retrieves a prompt by its ID for the given user.
    Raises HTTPException 404 if not found.
    """
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id,
                                     Prompt.user_id == user.id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


def delete_prompt(db: Session, user: User, prompt_id: UUID):
    """
    Deletes a prompt by its ID for the given user.
    """
    prompt = get_prompt_by_id(db, user, prompt_id)
    db.delete(prompt)
    db.commit()


def regenerate_prompt(db: Session, user: User, prompt_id: UUID, new_text: str) -> Prompt:
    """
    Regenerates an optimized prompt and explanation for a given prompt ID using new text.
    Updates the existing Prompt object in the database.
    """
    prompt = get_prompt_by_id(db, user, prompt_id)

    response = openai.chat.completions.create(
        model='gpt-4',
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": new_text}
        ]
    )
    content = response.choices[0].message.content
    total_tokens = response.usage.total_tokens

    optimized = content.strip()
    explanation = None
    if "\n\nExplicación:" in content:
        try:
            optimized, explanation = content.split("\n\nExplicación:", 1)
            optimized = optimized.strip()
            explanation = explanation.strip()
        except ValueError:
            pass

    prompt.original_prompt = new_text
    prompt.optimized_prompt = optimized
    prompt.explanation = explanation.strip() if explanation else None
    prompt.total_tokens = total_tokens
    db.commit()
    db.refresh(prompt)
    return prompt


def toggle_favorite_prompt(db: Session, user: User, prompt_id: UUID, favorite: bool) -> Prompt:
    """
    Sets or unsets a prompt as favorite for the given user.
    Returns the updated Prompt object.
    """
    prompt = get_prompt_by_id(db, user, prompt_id)
    prompt.is_favorite = favorite
    db.commit()
    db.refresh(prompt)
    return prompt


def list_favorite_prompts(db: Session, user: User) -> list[Prompt]:
    """
    Returns a list of all favorite prompts for the given user, ordered by creation date (descending).
    """
    return db.query(Prompt).filter(Prompt.user_id == user.id, Prompt.is_favorite == True).order_by(Prompt.created_at.desc()).all()
