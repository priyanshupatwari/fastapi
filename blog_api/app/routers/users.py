from fastapi import APIRouter, HTTPException, status, Depends

from app.database import supabase
from app.models.user import UserResponse
from app.dependencies.auth import get_current_user
from app.crud.user import get_user_by_id


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    """Get a user's public profile by their UUID."""
    user = get_user_by_id(supabase, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found"
        )
    return user
