from typing import Optional
from supabase import Client


def get_user_by_id(db: Client, user_id: str) -> Optional[dict]:
    result = db.table("profiles").select("*").eq("id", user_id).execute()
    return result.data[0] if result.data else None


def get_user_by_email(db: Client, email: str) -> Optional[dict]:
    result = db.table("profiles").select("*").eq("email", email).execute()
    return result.data[0] if result.data else None


def create_user_profile(db: Client, user_id: str, username: str, email: str) -> dict:
    """
    Creates the row in public.profiles after Supabase Auth creates the auth.users row.
    Must use the admin client because the user has no session yet (RLS would block the insert).
    """
    result = db.table("profiles").insert({
        "id": user_id,
        "username": username,
        "email": email,
    }).execute()
    return result.data[0]
