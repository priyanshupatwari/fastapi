from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from gotrue.errors import AuthApiError

from app.database import supabase, supabase_admin
from app.models.user import UserCreate, UserResponse, Token
from app.crud.user import get_user_by_email, create_user_profile, get_user_by_id
from app.dependencies.auth import create_access_token, get_current_user


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate):
    """
    Register a new user.

    Steps:
    1. Check the email isn't already taken
    2. Create the auth user in Supabase Auth (Supabase handles password hashing)
    3. Create the profile row in public.profiles
    4. Return a JWT so the user is immediately logged in after registering
    """
    # Step 1 — check for duplicate email
    existing = get_user_by_email(supabase_admin, user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )

    # Step 2 — create the auth user in Supabase Auth
    # Create the user in Supabase Auth (auth.users). Supabase Auth (GoTrue)
    # manages authentication fields (hashed password, confirmation, provider
    # info). The returned object is stored in `auth_response` and contains
    # `auth_response.user` (the auth user's record) and session info when
    # applicable.
    try:
        auth_response = supabase_admin.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
        })
    except AuthApiError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not auth_response.user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed — Supabase Auth did not return a user"
        )

    # Step 3 — create the profile in `public.profiles` (application data).
    # `auth.users` (managed by Supabase Auth) is separate from the app's
    # `profiles` table. We use the auth user's id as the profile id to link
    # the two records. Because the new user has no session yet, the admin
    # client (`supabase_admin`) is used to bypass RLS for this insert.
    user_id = str(auth_response.user.id)
    create_user_profile(
        db=supabase_admin,
        user_id=user_id,
        username=user_data.username,
        email=user_data.email,
    )

    # Step 4 — return a JWT
    access_token = create_access_token(data={"sub": user_id})
    return Token(access_token=access_token)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login and receive a JWT.

    Uses OAuth2PasswordRequestForm — expects form data (not JSON):
      - `username` field — we treat this as the email address
      - `password` field — the user's password

    The field is called 'username' because that's what the OAuth2 spec requires.
    We use it for the email address.
    """
    # Sign in via Supabase Auth — returns an auth response containing the
    # authenticated user (`auth_response.user`). We then take
    # `auth_response.user.id` and issue a JWT for our API (`create_access_token`).
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": form_data.username,   # OAuth2 spec calls it username; we use it as email
            "password": form_data.password,
        })
    except AuthApiError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = str(auth_response.user.id)
    access_token = create_access_token(data={"sub": user_id})
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserResponse = Depends(get_current_user)):
    """Returns the currently authenticated user's profile. Requires a valid JWT."""
    return current_user
