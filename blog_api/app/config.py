from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Single instance — import `settings` everywhere else
settings = Settings()
