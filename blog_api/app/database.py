from supabase import create_client, Client
from app.config import settings


def get_supabase() -> Client:
    """Anon client — respects Row Level Security. Use for all normal operations."""
    return create_client(settings.supabase_url, settings.supabase_anon_key)


def get_supabase_admin() -> Client:
    """Service role client — bypasses RLS. Use only for server-side admin tasks."""
    return create_client(settings.supabase_url, settings.supabase_service_key)


# Module-level singletons — import `supabase` or `supabase_admin` directly
supabase: Client = get_supabase()
supabase_admin: Client = get_supabase_admin()
