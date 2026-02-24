from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class BlogBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    body: str = Field(..., min_length=10)
    published: bool = True


class BlogCreate(BlogBase):
    pass   # Inherits title, body, published from BlogBase
           # author_id is taken from the JWT, not the request body


class BlogUpdate(BaseModel):
    # All fields are optional — PATCH only sends what changed
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    body: Optional[str] = Field(None, min_length=10)
    published: Optional[bool] = None


class BlogResponse(BlogBase):
    id: UUID
    author_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True   # Lets Pydantic read from dicts (Supabase returns dicts)
