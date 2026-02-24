from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, blogs, users


app = FastAPI(
    title="Blog API",
    description="A full-featured blog API with JWT authentication and Supabase",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — controls which frontend origins can call this API
# In production, replace with your actual frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(auth.router)
app.include_router(blogs.router)
app.include_router(users.router)


@app.get("/", tags=["Health"])
def health_check():
    """Basic health check. Confirms the API is running."""
    return {"status": "ok"}
