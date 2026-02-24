from typing import Optional
from supabase import Client
from app.models.blog import BlogCreate, BlogUpdate


def get_blog(db: Client, blog_id: str) -> Optional[dict]:
    """Get a single blog by ID. Returns None if not found."""
    result = db.table("blogs").select("*").eq("id", blog_id).execute()
    return result.data[0] if result.data else None


def get_blogs(
    db: Client,
    skip: int = 0,
    limit: int = 20,
    published_only: bool = True
) -> list[dict]:
    """Get a paginated list of blogs, optionally filtered to published only."""
    query = db.table("blogs").select("*, profiles(username)")

    if published_only:
        query = query.eq("published", True)

    result = (
        query
        .order("created_at", desc=True)
        .range(skip, skip + limit - 1)
        .execute()
    )
    return result.data


def get_blogs_by_author(db: Client, author_id: str) -> list[dict]:
    """Get all blogs by a specific author, including unpublished ones."""
    result = (
        db.table("blogs")
        .select("*")
        .eq("author_id", author_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


def create_blog(db: Client, blog: BlogCreate, author_id: str) -> dict:
    """Insert a new blog. Returns the created record."""
    payload = {
        **blog.model_dump(),   # unpacks: title, body, published
        "author_id": author_id,
    }
    result = db.table("blogs").insert(payload).execute()
    return result.data[0]


def update_blog(db: Client, blog_id: str, blog: BlogUpdate) -> Optional[dict]:
    """Partially update a blog. Only updates fields that were provided (non-None)."""
    payload = blog.model_dump(exclude_none=True)

    if not payload:
        # Nothing was sent — return the existing record unchanged
        return get_blog(db, blog_id)

    result = db.table("blogs").update(payload).eq("id", blog_id).execute()
    return result.data[0] if result.data else None


def delete_blog(db: Client, blog_id: str) -> bool:
    """Delete a blog. Returns True if deleted, False if the record didn't exist."""
    result = db.table("blogs").delete().eq("id", blog_id).execute()
    return len(result.data) > 0
