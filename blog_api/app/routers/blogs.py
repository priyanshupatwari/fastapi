from fastapi import APIRouter, HTTPException, status, Depends

from app.database import supabase
from app.models.blog import BlogCreate, BlogUpdate, BlogResponse
from app.models.user import UserResponse
from app.dependencies.auth import get_current_user
from app.crud import blog as crud_blog


router = APIRouter(prefix="/blogs", tags=["Blogs"])


@router.get("/", response_model=list[BlogResponse])
def get_blogs(skip: int = 0, limit: int = 20):
    """Get a paginated list of published blogs. Public — no auth required."""
    return crud_blog.get_blogs(supabase, skip=skip, limit=limit)


@router.get("/me", response_model=list[BlogResponse])
def get_my_blogs(current_user: UserResponse = Depends(get_current_user)):
    """Get all blogs (including unpublished drafts) by the logged-in user."""
    return crud_blog.get_blogs_by_author(supabase, author_id=str(current_user.id))


@router.get("/{blog_id}", response_model=BlogResponse)
def get_blog(blog_id: str):
    """Get a single blog by its UUID. Public — no auth required."""
    blog = crud_blog.get_blog(supabase, blog_id)
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with id '{blog_id}' not found"
        )
    return blog


@router.post("/", response_model=BlogResponse, status_code=status.HTTP_201_CREATED)
def create_blog(
    blog: BlogCreate,
    current_user: UserResponse = Depends(get_current_user),
):
    """Create a new blog post. Requires authentication. author_id is set from the JWT."""
    return crud_blog.create_blog(supabase, blog=blog, author_id=str(current_user.id))


@router.patch("/{blog_id}", response_model=BlogResponse)
def update_blog(
    blog_id: str,
    blog: BlogUpdate,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Partially update a blog. Only the author can update their own blogs.
    Only send the fields you want to change — all others remain unchanged.
    """
    existing = crud_blog.get_blog(supabase, blog_id)

    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")

    if str(existing["author_id"]) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the author of this blog"
        )

    updated = crud_blog.update_blog(supabase, blog_id=blog_id, blog=blog)
    return updated


@router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(
    blog_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Delete a blog. Only the author can delete their own blogs.
    Returns 204 No Content on success — no response body.
    """
    existing = crud_blog.get_blog(supabase, blog_id)

    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")

    if str(existing["author_id"]) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the author of this blog"
        )

    crud_blog.delete_blog(supabase, blog_id)
    # No return value — 204 means empty body
