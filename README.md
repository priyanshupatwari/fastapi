# FastAPI Blog API — Complete Reference
### Core Concepts + Full Project Walkthrough | JWT Auth + Supabase

> **What this file covers**
> Everything in one place: how FastAPI works, how the Blog API is structured, and a full walkthrough of every route — what gets called, in what order, and what comes back at each step.

---

## Table of Contents

**Part 1 — Core Concepts**
1. [What is FastAPI & How it Thinks](#1-what-is-fastapi--how-it-thinks)
2. [Installation & First Server](#2-installation--first-server)
3. [Your First Endpoints](#3-your-first-endpoints)
4. [Path Parameters](#4-path-parameters)
5. [Query Parameters](#5-query-parameters)
6. [Request Bodies & Pydantic](#6-request-bodies--pydantic)
7. [Status Codes](#7-status-codes)
8. [Exception Handling](#8-exception-handling)
9. [Response Models — Filtering Output](#9-response-models--filtering-output)
10. [APIRouters — Splitting Routes](#10-apirouters--splitting-routes)
11. [Dependencies — Depends()](#11-dependencies--depends)
12. [Middleware — Request Lifecycle Interception](#12-middleware--request-lifecycle-interception)
13. [Quick Reference Cheatsheet](#13-quick-reference-cheatsheet)

**Part 2 — The Blog API Project**
14. [Project Structure & Layers](#14-project-structure--layers)
15. [Supabase Setup](#15-supabase-setup)
16. [Config & Environment Variables](#16-config--environment-variables)
17. [Pydantic Schemas](#17-pydantic-schemas)
18. [Database Layer](#18-database-layer)
19. [CRUD Functions — Call Signatures & Returns](#19-crud-functions--call-signatures--returns)
20. [Auth Dependency Chain](#20-auth-dependency-chain)
21. [Route Walkthroughs — Every Endpoint](#21-route-walkthroughs--every-endpoint)
22. [App Startup & Wiring](#22-app-startup--wiring)
23. [Running, Testing & Debugging](#23-running-testing--debugging)
24. [Error Reference](#24-error-reference)

---

# Part 1 — Core Concepts

---

## 1. What is FastAPI & How it Thinks

FastAPI is a modern Python web framework for building APIs. It requires Python 3.10+ and leans heavily on Python's **type hints** — that single design choice is what gives FastAPI its three superpowers:

**Automatic validation.** You declare that a field must be an integer, FastAPI rejects anything that isn't — automatically, with a clear error message. You write zero validation code yourself.

**Automatic documentation.** Visit `/docs` and you get a fully interactive Swagger UI. Visit `/redoc` for an alternative view. Both are generated from your code and stay in sync automatically.

**Editor intelligence.** Because everything is typed, your editor knows the shape of every object. Autocomplete and inline errors work perfectly throughout.

### The mental model

```
Request comes in
    → FastAPI reads your type hints
    → Validates & parses the incoming data
    → Calls your function with clean, typed Python objects
    → Serializes the return value back to JSON
    → Sends the response
```

You write the shape of the data and the business logic. FastAPI handles the rest.

### What FastAPI is built on

| Layer | Library | Does what |
|---|---|---|
| HTTP server | Starlette | Routing, middleware, WebSockets |
| Data validation | Pydantic | Schema definition, parsing, serialization |
| ASGI server | Uvicorn | Runs the app (like Gunicorn but async) |

---

## 2. Installation & First Server

### Step 1 — Virtual environment

Always use a virtual environment. It keeps this project's packages isolated from your system Python.

```bash
# Create the venv
python -m venv venv

# Activate it
source venv/bin/activate        # Mac / Linux
venv\Scripts\activate           # Windows (Command Prompt)
.\venv\Scripts\Activate.ps1     # Windows (PowerShell)

# You should see (venv) at the start of your prompt
```

### Step 2 — Install packages

```bash
pip install fastapi uvicorn[standard]
```

### Step 3 — Hello World

Create `main.py`:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}
```

Start the server:

```bash
uvicorn main:app --reload
```

- `main` → the file `main.py`
- `app` → the `FastAPI()` instance inside it
- `--reload` → restart the server on file save (dev only — remove in production)

Open [http://localhost:8000](http://localhost:8000) → `{"message": "Hello World"}`
Open [http://localhost:8000/docs](http://localhost:8000/docs) → Swagger UI, already working.

---

## 3. Your First Endpoints

An endpoint is a function decorated with an HTTP method decorator. FastAPI calls it when a request hits that path.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/about")
def about():
    return {"app": "Blog API", "version": "1.0"}

# You can return dicts, Pydantic models, lists — FastAPI serializes them all
@app.get("/items")
def get_items():
    return [
        {"id": 1, "title": "First item"},
        {"id": 2, "title": "Second item"},
    ]
```

**Key point:** The function name doesn't matter to FastAPI. The decorator (`@app.get`, `@app.post`, etc.) and the path string (`"/"`, `"/items"`) are what define the route.

### HTTP method decorators

| Decorator | Typical use |
|---|---|
| `@app.get` | Read / retrieve data |
| `@app.post` | Create a new resource |
| `@app.put` | Replace a resource entirely |
| `@app.patch` | Partially update a resource |
| `@app.delete` | Delete a resource |

---

## 4. Path Parameters

Path parameters are dynamic segments of the URL, declared with curly braces in the path and as function arguments.

```python
@app.get("/blog/{id}")
def get_blog(id: int):
    return {"blog_id": id}
```

**What the type hint does:** If you declare `id: int`, FastAPI automatically:
- Rejects requests where `id` is not a valid integer (returns `422`)
- Converts the string from the URL into an actual Python `int` before calling your function

```bash
GET /blog/42        → {"blog_id": 42}          ✅
GET /blog/abc       → 422 Unprocessable Entity  ❌ (not an int)
```

### Multiple path parameters

```python
@app.get("/users/{user_id}/posts/{post_id}")
def get_user_post(user_id: int, post_id: int):
    return {"user_id": user_id, "post_id": post_id}
```

### Order matters — specific routes before dynamic ones

```python
# ✅ Correct order
@app.get("/blog/featured")       # This must come FIRST
def get_featured():
    return {"blog": "featured"}

@app.get("/blog/{id}")           # Otherwise this catches 'featured' as an id
def get_blog(id: int):
    return {"blog_id": id}
```

FastAPI matches routes top-to-bottom. A dynamic route will swallow any static segment in the same position if it's registered first.

### Enum path parameters — restrict to specific values

```python
from enum import Enum

class Category(str, Enum):
    technology = "technology"
    science = "science"
    sports = "sports"

@app.get("/blog/category/{cat}")
def get_by_category(cat: Category):
    return {"category": cat.value}
```

Now `/blog/category/cooking` returns a `422`. Only the three defined values are accepted.

---

## 5. Query Parameters

Query parameters appear after the `?` in the URL. Any function argument that isn't a path parameter and isn't a Pydantic model is treated as a query parameter by FastAPI.

```python
@app.get("/blog")
def get_blogs(limit: int = 10, published: bool = True):
    return {"limit": limit, "published": published}
```

```bash
GET /blog                          → limit=10, published=True   (defaults)
GET /blog?limit=5                  → limit=5,  published=True
GET /blog?limit=5&published=false  → limit=5,  published=False
```

### Optional query parameters

```python
from typing import Optional

@app.get("/blog")
def get_blogs(limit: int = 10, search: Optional[str] = None):
    if search:
        return {"results": f"Searching for: {search}"}
    return {"limit": limit}
```

### Type conversion is automatic

FastAPI converts query strings to the right Python type:

| Query string value | Python type |
|---|---|
| `"true"` / `"1"` / `"yes"` | `True` (bool) |
| `"false"` / `"0"` / `"no"` | `False` (bool) |
| `"10"` | `10` (int) |

### Combining path and query parameters

```python
@app.get("/users/{user_id}/posts")
def get_user_posts(user_id: int, skip: int = 0, limit: int = 20):
    return {"user_id": user_id, "skip": skip, "limit": limit}
```

`user_id` is a path param (in the URL pattern). `skip` and `limit` are query params (not in the URL pattern).

---

## 6. Request Bodies & Pydantic

A **request body** is data the client sends to your API, usually as JSON in a POST/PATCH request. You define what you expect using a Pydantic model.

### Your first Pydantic model

```python
from pydantic import BaseModel
from typing import Optional

class BlogCreate(BaseModel):
    title: str
    body: str
    published: bool = True            # Optional with default
    tags: Optional[list[str]] = None  # Completely optional
```

Use it in a route:

```python
@app.post("/blog")
def create_blog(blog: BlogCreate):
    # `blog` is a fully validated Python object here
    # blog.title, blog.body, blog.published are all typed correctly
    return {"created": blog.title}
```

FastAPI knows `blog` is a request body (not a path or query param) because its type is a Pydantic model.

### How FastAPI distinguishes parameter types

| Parameter type | Where FastAPI looks | How to declare |
|---|---|---|
| Path param | URL path `{id}` | Function arg with same name |
| Query param | URL `?key=val` | Function arg with default or `Optional` |
| Request body | JSON body | Function arg typed as a Pydantic model |

### What Pydantic gives you automatically

```python
# ✅ Valid request body:
# {"title": "My Post", "body": "Content here"}
# → FastAPI calls your function with a BlogCreate object

# ❌ Missing required field:
# {"body": "Content here"}
# → 422: {"detail": [{"loc": ["body", "title"], "msg": "field required"}]}

# ❌ Wrong type:
# {"title": 123, "body": "Content"}
# → FastAPI coerces 123 to "123" if possible (it is for str), otherwise 422
```

### Field validation with `Field()`

```python
from pydantic import BaseModel, Field

class BlogCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    body: str = Field(..., min_length=10)
    published: bool = Field(True, description="Whether the post is public")
```

`...` means the field is required (no default). Named arguments add validation rules. Everything appears in `/docs` automatically.

### Receiving body + path param in the same route

```python
@app.put("/blog/{blog_id}")
def update_blog(blog_id: int, blog: BlogCreate):
    # blog_id → from URL path
    # blog    → from request body (JSON)
    return {"updated_id": blog_id, "new_title": blog.title}
```

### `model_dump()` — converting a schema to a dict

```python
blog = BlogCreate(title="My First Post", body="This is content")

blog.model_dump()
# {"title": "My First Post", "body": "This is content", "published": True}

blog.model_dump(exclude_none=True)
# Same result, but skips any field whose value is None — useful for PATCH operations
```

---

## 7. Status Codes

By default, successful routes return `200 OK`. Change it with `status_code` in the decorator.

```python
from fastapi import status

@app.post("/blog", status_code=status.HTTP_201_CREATED)
def create_blog(blog: BlogCreate):
    return {"message": "Blog created"}

@app.delete("/blog/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(id: int):
    return None   # 204 = empty body
```

### The status codes you'll use most

| Constant | Code | When to use |
|---|---|---|
| `HTTP_200_OK` | 200 | Default. Data returned successfully. |
| `HTTP_201_CREATED` | 201 | Resource was created (POST). |
| `HTTP_204_NO_CONTENT` | 204 | Success but no response body (DELETE). |
| `HTTP_400_BAD_REQUEST` | 400 | Client sent something invalid. |
| `HTTP_401_UNAUTHORIZED` | 401 | Not authenticated — no valid token. |
| `HTTP_403_FORBIDDEN` | 403 | Authenticated but not allowed to do this. |
| `HTTP_404_NOT_FOUND` | 404 | Resource doesn't exist. |
| `HTTP_422_UNPROCESSABLE_ENTITY` | 422 | Pydantic validation failed (raised automatically). |
| `HTTP_500_INTERNAL_SERVER_ERROR` | 500 | Something crashed on the server. |

**Always use `status.HTTP_*` constants** instead of raw numbers. They're self-documenting and less error-prone.

---

## 8. Exception Handling

When something goes wrong, raise an `HTTPException`. FastAPI catches it and returns the right JSON error response.

```python
from fastapi import FastAPI, HTTPException, status

@app.get("/blog/{id}")
def get_blog(id: int):
    blog = fetch_from_db(id)

    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with id {id} not found"
        )

    return blog
```

The client receives:
```json
{
  "detail": "Blog with id 99 not found"
}
```

### Custom exception headers

Some situations (like auth failures) require custom headers:

```python
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
```

### When to raise which exception

| Situation | Exception |
|---|---|
| Record not found in DB | `404 Not Found` |
| User not logged in | `401 Unauthorized` |
| User logged in but not allowed | `403 Forbidden` |
| Client sent bad data (outside Pydantic) | `400 Bad Request` |
| Duplicate record (e.g., email already exists) | `400 Bad Request` |

**Never catch exceptions silently.** Let them bubble up with the right status code — your API clients depend on accurate status codes to know what to do next.

---

## 9. Response Models — Filtering Output

A **response model** tells FastAPI exactly what shape the response should have. Important for two reasons:

1. **Security** — you never accidentally return a password, internal ID, or sensitive field
2. **Consistency** — the response shape is guaranteed regardless of what's in the DB

### The problem without response models

```python
# Without a response model, this could return the password hash!
@app.get("/users/{id}")
def get_user(id: str):
    user = db.get_user(id)    # returns {"id": "...", "email": "...", "hashed_password": "..."}
    return user               # ❌ password hash exposed!
```

### The fix — declare `response_model`

```python
from pydantic import BaseModel

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    # No hashed_password — it's not in this model, so it never goes out

@app.get("/users/{id}", response_model=UserResponse)
def get_user(id: str):
    user = db.get_user(id)
    return user    # FastAPI filters to only the fields in UserResponse ✅
```

### Response model for lists

```python
@app.get("/users", response_model=list[UserResponse])
def get_users():
    return db.get_all_users()
```

### `from_attributes = True`

Add this to any response schema when the data source is a dict (as Supabase always returns). It lets Pydantic read dict keys the same way it reads object attributes.

### Naming convention for schemas

| Suffix | Purpose | Example |
|---|---|---|
| `Base` | Shared fields (extended by others) | `BlogBase` |
| `Create` | Fields needed to create a resource | `BlogCreate` |
| `Update` | Fields for partial updates (all optional) | `BlogUpdate` |
| `Response` | What the API returns | `BlogResponse` |

---

## 10. APIRouters — Splitting Routes

As your app grows, putting everything in `main.py` becomes unmanageable. `APIRouter` lets you move related routes into separate files and mount them on the main app.

### Before — everything in `main.py` (don't do this)

```python
@app.get("/blogs")
def get_blogs(): ...

@app.post("/blogs")
def create_blog(): ...

@app.get("/users")
def get_users(): ...

@app.post("/auth/login")
def login(): ...
# 400 more lines...
```

### After — routes in separate files

**`routers/blogs.py`:**

```python
from fastapi import APIRouter

router = APIRouter(
    prefix="/blogs",    # All routes here get /blogs prepended automatically
    tags=["Blogs"],     # Groups these routes under "Blogs" in /docs
)

@router.get("/")           # → GET /blogs/
def get_blogs(): ...

@router.get("/{blog_id}")  # → GET /blogs/{blog_id}
def get_blog(blog_id: str): ...

@router.post("/")          # → POST /blogs/
def create_blog(): ...
```

**`main.py`:**

```python
from fastapi import FastAPI
from routers import blogs, auth, users

app = FastAPI()

app.include_router(auth.router)
app.include_router(blogs.router)
app.include_router(users.router)
```

### What `prefix` and `tags` do

- `prefix="/blogs"` means you write `@router.get("/{id}")` and FastAPI registers it as `GET /blogs/{id}` — no repetition
- `tags=["Blogs"]` groups all these endpoints visually under a "Blogs" section in Swagger UI

---

## 11. Dependencies — Depends()

`Depends()` is FastAPI's dependency injection system. You write a reusable function once, then inject it into any route. FastAPI calls it automatically before your route handler runs.

### Basic pattern — reusable pagination

```python
from fastapi import Depends

# A dependency is just a regular function
def get_pagination(skip: int = 0, limit: int = 20) -> dict:
    return {"skip": skip, "limit": limit}

@router.get("/")
def get_blogs(page: dict = Depends(get_pagination)):
    # FastAPI called get_pagination(), passed the result as `page`
    return {"skip": page["skip"], "limit": page["limit"]}

# GET /blogs?skip=20&limit=10 now works — no copy-paste
```

### Auth dependency — the most important use case

```python
# get_current_user is defined once and reused across many routes:
@router.post("/")
def create_blog(
    blog: BlogCreate,
    current_user: UserResponse = Depends(get_current_user),
):
    # If no valid token → get_current_user raises 401 before this line runs
    # If valid token → current_user is the authenticated user object
    ...
```

### Dependency chains

Dependencies can themselves depend on other things. FastAPI resolves the full chain automatically:

```
oauth2_scheme (reads Bearer token from header)
    → get_current_user (validates the token, fetches the user)
        → your route handler (gets the clean user object)
```

You declare only the last step in each route. FastAPI calls all the preceding steps.

### Optional authentication

Some routes are public but show more data to logged-in users. Use `auto_error=False` on the `OAuth2PasswordBearer` so it returns `None` instead of raising `401` when no token is provided. Your dependency then checks if the token is `None` and returns `None` for the user instead of rejecting the request.

---

## 12. Middleware — Request Lifecycle Interception

Middleware sits between the web server and your route handlers. It intercepts **every request before it reaches any route** and **every response before it leaves the server**. Unlike `Depends()`, which is opt-in per-route, middleware runs on **all requests unconditionally**.

```
Client Request
    → Middleware (runs first — can read/modify the request)
        → Route Handler (your endpoint runs here)
    ← Middleware (runs again — can read/modify the response)
← Client Response
```

### How to write middleware in FastAPI

FastAPI (via Starlette) provides `BaseHTTPMiddleware`. Subclass it and override `dispatch`:

```python
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # ── Before the route handler ──────────────────────────────
        print(f"→ {request.method}  {request.url.path}")
        start = time.perf_counter()

        response = await call_next(request)  # ← route handler runs here

        # ── After the route handler ───────────────────────────────
        duration_ms = (time.perf_counter() - start) * 1000
        print(f"← {response.status_code}  {request.method}  {request.url.path}  {duration_ms:.1f}ms")

        return response
```

Register it on the app — order matters, last registered runs outermost:

```python
app.add_middleware(RequestLoggingMiddleware)
```

### Middleware vs. Dependency Injection

| | Middleware | `Depends()` |
|---|---|---|
| **Runs on** | Every request globally | Only routes that declare it |
| **Typical use** | Logging, CORS, rate limiting, timing | Auth, pagination, validation |
| **Can access response** | Yes — wraps the entire handler | No |
| **Route-specific** | No | Yes |

Use middleware for **cross-cutting concerns** that apply uniformly (logging, CORS, compression). Use `Depends()` for **route-specific logic** like authentication.

### Execution order of multiple middlewares

FastAPI processes middleware in **reverse registration order** (last added = outermost wrapper):

```python
app.add_middleware(CORSMiddleware)        # ← registered first = runs second (inner)
app.add_middleware(RequestLoggingMiddleware)  # ← registered second = runs first (outer)
```

For each request: `RequestLoggingMiddleware.before → CORSMiddleware.before → route handler → CORSMiddleware.after → RequestLoggingMiddleware.after`

---

## 13. Quick Reference Cheatsheet

### Pydantic

```python
# Define
class Item(BaseModel):
    name: str
    price: float = Field(..., gt=0)         # Required, must be > 0
    tags: list[str] = []                    # Optional list with empty default
    note: Optional[str] = None              # Nullable optional

# Convert
item.model_dump()                           # → dict, all fields
item.model_dump(exclude_none=True)          # → dict, skip None fields
item.model_dump(include={"name", "price"})  # → dict, only these fields

# Validate from dict
Item.model_validate({"name": "Shoe", "price": 49.99})
```

### Route patterns

```python
@router.get("/{id}")                        # Path param
def read(id: str): ...

@router.get("/")                            # Query params (from function args with defaults)
def list(skip: int = 0, q: Optional[str] = None): ...

@router.post("/")                           # Request body (Pydantic model)
def create(item: ItemCreate): ...

@router.patch("/{id}")                      # Body + path + auth dependency
def update(id: str, item: ItemUpdate, user = Depends(get_current_user)): ...

@router.delete("/{id}", status_code=204)    # 204 = no response body
def delete(id: str): ...
```

### Exception patterns

```python
raise HTTPException(status_code=404, detail="Not found")
raise HTTPException(status_code=403, detail="Forbidden")
raise HTTPException(
    status_code=401,
    detail="Unauthorized",
    headers={"WWW-Authenticate": "Bearer"}
)
```

### JWT lifecycle

```python
# 1. Create (on login/register)
token = create_access_token({"sub": str(user_id)})

# 2. Client attaches it to every request
# Authorization: Bearer eyJhbGci...

# 3. Server decodes it on each protected request
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
user_id = payload.get("sub")

# 4. Token expires automatically — client re-logs in to get a new token
```

---

# Part 2 — The Blog API Project

---

## 14. Project Structure & Layers

```
blog_api/
│
├── app/
│   ├── __init__.py            # empty — marks this as a Python package
│   ├── main.py                # Creates FastAPI(), registers routers, CORS + logging middleware
│   ├── config.py              # Reads .env file, exposes typed `settings` object
│   ├── database.py            # Supabase clients. Created once, imported everywhere.
│   │
│   ├── models/                # Pydantic schemas — defines the shape of data at API boundaries
│   │   ├── __init__.py
│   │   ├── user.py            # UserCreate, UserResponse, Token, TokenData
│   │   └── blog.py            # BlogCreate, BlogUpdate, BlogResponse
│   │
│   ├── routers/               # HTTP route handlers grouped by resource
│   │   ├── __init__.py
│   │   ├── auth.py            # POST /auth/register, POST /auth/login, GET /auth/me
│   │   ├── users.py           # GET /users/{id}
│   │   └── blogs.py           # Full CRUD: GET/POST/PATCH/DELETE /blogs/...
│   │
│   ├── crud/                  # Pure database operations — no HTTP, no HTTPException
│   │   ├── __init__.py
│   │   ├── user.py            # get_user_by_id, get_user_by_email, create_user_profile
│   │   └── blog.py            # get_blog, get_blogs, create_blog, update_blog, delete_blog
│   │
│   ├── dependencies/          # FastAPI Depends() functions
│   │   ├── __init__.py
│   │   └── auth.py            # create_access_token, decode_access_token, get_current_user
│   │
│   └── middleware/            # Starlette BaseHTTPMiddleware classes
│       ├── __init__.py
│       └── logging_middleware.py  # RequestLoggingMiddleware — logs every request
│
├── .env                       # Secret keys — NEVER commit to git
├── .env.example               # Template with placeholder values — safe to commit
├── .gitignore
└── requirements.txt
```

### The rule of each layer

Data always flows in one direction: inward. Nothing in a lower layer ever imports from a higher one.

```
Request → routers → dependencies / crud → database → models / config → .env
```

| Layer | File(s) | Knows about | Does NOT know about |
|---|---|---|---|
| Entry point | `main.py` | Routers, middleware | Business logic |
| Middleware | `middleware/*.py` | HTTP request/response | Business logic, DB, models |
| Route handlers | `routers/*.py` | HTTP + crud + dependencies | How the database works internally |
| Auth dependency | `dependencies/auth.py` | JWT, DB, models | Business logic |
| Database ops | `crud/*.py` | Supabase client + models | HTTP requests, HTTPException |
| DB clients | `database.py` | `config.settings` | Everything else |
| Schemas | `models/*.py` | Pydantic only | Database, HTTP, business logic |
| Config | `config.py` | `.env` file | Everything else — imports nothing from the app |

**Why this separation?**
- Testing `crud/` doesn't need an HTTP server — just pass a DB client
- Swapping Supabase for Postgres only touches `crud/` and `database.py`
- Adding a new resource = create `models/new.py` + `crud/new.py` + `routers/new.py`. Nothing else changes.

### Complete import dependency map

```
main.py
  └── imports → routers/auth.py, routers/blogs.py, routers/users.py

routers/auth.py
  ├── imports → models/user.py       (UserCreate, Token, UserResponse)
  ├── imports → crud/user.py         (get_user_by_email, create_user_profile)
  ├── imports → dependencies/auth.py (create_access_token, get_current_user)
  └── imports → database.py          (supabase, supabase_admin)

routers/blogs.py
  ├── imports → models/blog.py       (BlogCreate, BlogUpdate, BlogResponse)
  ├── imports → models/user.py       (UserResponse)
  ├── imports → crud/blog.py         (via `from app.crud import blog as crud_blog`)
  ├── imports → dependencies/auth.py (get_current_user)
  └── imports → database.py          (supabase)

routers/users.py
  ├── imports → models/user.py       (UserResponse)
  ├── imports → crud/user.py         (get_user_by_id)
  └── imports → database.py          (supabase)

dependencies/auth.py
  ├── imports → config.py            (settings)
  ├── imports → crud/user.py         (get_user_by_id)
  ├── imports → database.py          (supabase)
  └── imports → models/user.py       (TokenData, UserResponse)

crud/blog.py
  └── imports → models/blog.py       (BlogCreate, BlogUpdate)

crud/user.py
  └── (no app imports — only type hint: supabase Client)

database.py
  └── imports → config.py            (settings)

config.py
  └── (no app imports — reads from .env file)
```

---

## 15. Supabase Setup

### Create your project

1. Go to [supabase.com](https://supabase.com) → Sign up → New Project
2. Choose a region close to you, set a strong database password
3. Wait ~2 minutes for provisioning

### Get your credentials

Settings (gear icon) → API:
- **Project URL** — `https://xyzxyz.supabase.co`
- **anon public key** — respects Row Level Security; safe for normal app operations
- **service_role key** — bypasses all RLS; use only server-side for admin tasks (never expose to frontend)

### Create the database tables

Open the **SQL Editor** in Supabase and run:

```sql
-- Profiles table — public user data, linked to Supabase Auth
CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Blogs table
CREATE TABLE blogs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  published BOOLEAN DEFAULT TRUE,
  author_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Enable Row Level Security (RLS)

RLS means the database enforces access rules itself. Even if your app has a bug, the database won't return data it shouldn't.

```sql
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE blogs ENABLE ROW LEVEL SECURITY;

-- Profiles: users can only read/update their own profile
CREATE POLICY "Users can view own profile"
  ON profiles FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE USING (auth.uid() = id);

-- Blogs: anyone can read published blogs
CREATE POLICY "Public can read published blogs"
  ON blogs FOR SELECT USING (published = true);

-- Blogs: authenticated users can read their own unpublished blogs
CREATE POLICY "Authors can read own blogs"
  ON blogs FOR SELECT USING (auth.uid() = author_id);

-- Blogs: only the author can write/edit/delete
CREATE POLICY "Authors can insert blogs"
  ON blogs FOR INSERT WITH CHECK (auth.uid() = author_id);

CREATE POLICY "Authors can update own blogs"
  ON blogs FOR UPDATE USING (auth.uid() = author_id);

CREATE POLICY "Authors can delete own blogs"
  ON blogs FOR DELETE USING (auth.uid() = author_id);
```

> **anon key vs service_role key:**
> The `anon` key respects RLS. Use it for everything the logged-in user triggers.
> The `service_role` key bypasses RLS. Use it only server-side for admin operations (like creating a profile row on registration, before the user has a session).

### Auto-update `updated_at` on blog edits

```sql
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = NOW(); RETURN NEW; END; $$ LANGUAGE plpgsql;

CREATE TRIGGER blogs_updated_at
  BEFORE UPDATE ON blogs
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

---

## 16. Config & Environment Variables

### Install all project packages

```bash
pip install fastapi uvicorn[standard] pydantic pydantic-settings \
            supabase python-jose[cryptography] passlib[bcrypt] \
            python-multipart python-dotenv
pip freeze > requirements.txt
```

| Package | Why you need it |
|---|---|
| `fastapi` | The framework |
| `uvicorn[standard]` | The ASGI server that runs FastAPI |
| `pydantic` | Schema definitions and validation |
| `pydantic-settings` | Loads `.env` files into typed settings objects |
| `supabase` | Official Supabase Python client |
| `python-jose[cryptography]` | Create and verify JWTs |
| `passlib[bcrypt]` | Hash and verify passwords |
| `python-multipart` | Required for OAuth2 login forms |
| `python-dotenv` | Reads `.env` files |

### `.env` file contents

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Generate a strong `SECRET_KEY`: `openssl rand -hex 32`

Add `.env` to `.gitignore` immediately: `echo ".env" >> .gitignore`

### What `app/config.py` does

`config.py` defines a `Settings` class that extends `pydantic-settings`' `BaseSettings`. It declares six typed fields: `supabase_url`, `supabase_anon_key`, `supabase_service_key`, `secret_key`, `algorithm` (default `"HS256"`), and `access_token_expire_minutes` (default `60`). The inner `Config` class tells it to read from `.env`.

A single `settings` instance is created at module level. **If any required variable is missing, the app crashes here at startup with a clear error** naming the missing variable — you catch misconfigured environments before any request is ever served.

Everything else in the app imports `settings` from `app.config` and accesses keys like `settings.secret_key`. It's fully typed so autocomplete works.

---

## 17. Pydantic Schemas

Schemas live in `app/models/` and define the exact shape of data at every API boundary — what comes in from the client and what goes out.

### Blog schemas (`app/models/blog.py`)

| Schema | Fields | Purpose |
|---|---|---|
| `BlogBase` | `title` (str, 5–200 chars), `body` (str, 10+ chars), `published` (bool, default True) | Shared base; extended by Create and Response |
| `BlogCreate` | inherits `BlogBase` — no `author_id` | Body of `POST /blogs/`. Author is injected from the JWT, never from the request — this prevents impersonation |
| `BlogUpdate` | `title?`, `body?`, `published?` — all Optional | Body of `PATCH /blogs/{id}`. Only send what you want to change; omitted fields are ignored via `model_dump(exclude_none=True)` |
| `BlogResponse` | `BlogBase` + `id` (UUID), `author_id` (UUID), `created_at` (datetime), `updated_at` (datetime) | Shape of every blog object returned by the API. `from_attributes = True` lets Pydantic read from Supabase dicts |

### User schemas (`app/models/user.py`)

| Schema | Fields | Purpose |
|---|---|---|
| `UserBase` | `username` (str, 3–50 chars), `email` (EmailStr — validated format) | Shared base |
| `UserCreate` | `UserBase` + `password` (str, 8+ chars) | Body of `POST /auth/register` |
| `UserUpdate` | `username?` (Optional) | For future profile update endpoints |
| `UserResponse` | `id` (UUID), `username`, `email`, `created_at` | Safe public shape — never includes password or hash |
| `Token` | `access_token` (str), `token_type` (str, default `"bearer"`) | Returned by `/auth/register` and `/auth/login` |
| `TokenData` | `user_id` (Optional str) | Internal-only: carries the decoded `sub` claim out of `decode_access_token` |

---

## 18. Database Layer

### What `app/database.py` creates

Two Supabase client singletons are created at module level when the app starts:

- **`supabase`** — built with the anon key. Respects RLS. Used for all normal operations triggered by a logged-in user.
- **`supabase_admin`** — built with the service_role key. Bypasses RLS entirely. Used only for admin tasks where no user session exists yet (e.g., inserting a profile row during registration before the user has authenticated).

Both are imported directly by routers: `from app.database import supabase, supabase_admin`.

### How Supabase queries work

Every query is a method chain ending in `.execute()`. The result object always has a `.data` attribute that is **always a list of dicts**, never a single dict and never `None`.

| Operation | Chain | `.data` result |
|---|---|---|
| Select all | `.table("blogs").select("*").execute()` | List of all matching rows |
| Select one by id | `.table("blogs").select("*").eq("id", id).execute()` | List with 0 or 1 item — use `[0]` after checking it's non-empty |
| Insert | `.table("blogs").insert({...}).execute()` | List containing the newly created row |
| Update | `.table("blogs").update({...}).eq("id", id).execute()` | List containing the updated row |
| Delete | `.table("blogs").delete().eq("id", id).execute()` | List containing the deleted row |
| Join | `.table("blogs").select("*, profiles(username)").execute()` | Each row has a nested `profiles` dict |
| Pagination | `.range(skip, skip + limit - 1)` | Slices the result set (0-indexed, inclusive on both ends) |

**Always check `.data` is non-empty before accessing `[0]`.** For single-record lookups the CRUD functions do this for you and return `None` when nothing was found.

---

## 19. CRUD Functions — Call Signatures & Returns

CRUD functions are pure database operations with no HTTP logic. They accept a Supabase client and typed arguments, and return plain Python dicts or `None`. They never raise `HTTPException` — that job belongs to the routers.

### `app/crud/blog.py`

---

**`get_blog(db, blog_id)`**
- **Accepts:** anon Supabase client, `blog_id` as a string UUID
- **Queries:** `SELECT * FROM blogs WHERE id = blog_id`
- **Returns:** a dict of the blog row, or `None` if no row matched

---

**`get_blogs(db, skip, limit, published_only)`**
- **Accepts:** anon Supabase client; `skip` (default 0), `limit` (default 20), `published_only` (default True)
- **Queries:** `SELECT *, profiles(username) FROM blogs` optionally filtered to `published = true`, ordered by `created_at DESC`, paginated with `.range(skip, skip + limit - 1)`
- **Returns:** a list of blog dicts, each with a nested `profiles` object containing the author's username. Empty list if nothing matched.

---

**`get_blogs_by_author(db, author_id)`**
- **Accepts:** anon Supabase client, `author_id` as a string UUID
- **Queries:** `SELECT * FROM blogs WHERE author_id = author_id ORDER BY created_at DESC`
- **Returns:** a list of all the author's blog dicts — including unpublished/drafts. Empty list if none found.

---

**`create_blog(db, blog, author_id)`**
- **Accepts:** anon Supabase client, a `BlogCreate` schema object, `author_id` string from the JWT
- **Builds payload:** calls `blog.model_dump()` to get `{title, body, published}`, then merges in `author_id`. The `author_id` comes from the function argument (the JWT), never from the request body.
- **Queries:** `INSERT INTO blogs VALUES (payload)`
- **Returns:** a dict of the newly created blog row including its generated UUID, timestamps, and `author_id`

---

**`update_blog(db, blog_id, blog)`**
- **Accepts:** anon Supabase client, `blog_id` string, a `BlogUpdate` schema object
- **Builds payload:** calls `blog.model_dump(exclude_none=True)` — this strips any fields that weren't sent in the PATCH request, so only the changed fields reach the database
- **Short circuit:** if the payload is empty (nothing was sent), calls `get_blog` and returns the existing record unchanged
- **Queries:** `UPDATE blogs SET payload WHERE id = blog_id`
- **Returns:** a dict of the updated blog row, or `None` if the row disappeared between the check and the update

---

**`delete_blog(db, blog_id)`**
- **Accepts:** anon Supabase client, `blog_id` string
- **Queries:** `DELETE FROM blogs WHERE id = blog_id`
- **Returns:** `True` if a row was deleted, `False` if nothing matched (used internally; the router uses the earlier `get_blog` check for the 404 response)

---

### `app/crud/user.py`

---

**`get_user_by_id(db, user_id)`**
- **Accepts:** Supabase client (anon or admin), `user_id` string UUID
- **Queries:** `SELECT * FROM profiles WHERE id = user_id`
- **Returns:** a dict of the profile row (`id`, `username`, `email`, `created_at`), or `None` if not found

---

**`get_user_by_email(db, email)`**
- **Accepts:** Supabase client (usually admin for duplicate checks), `email` string
- **Queries:** `SELECT * FROM profiles WHERE email = email`
- **Returns:** a dict of the profile row, or `None` if not found. Used during registration to detect duplicate emails.

---

**`create_user_profile(db, user_id, username, email)`**
- **Accepts:** admin Supabase client (must be admin — the user has no session yet so RLS would block the anon client), `user_id` UUID string from Supabase Auth, `username`, `email`
- **Queries:** `INSERT INTO profiles VALUES ({id, username, email})`
- **Returns:** a dict of the newly created profile row
- **Why admin client:** Called during registration before any JWT is issued, meaning there is no authenticated Supabase session. The RLS policy on `profiles` would block an insert from the anon client.

---

## 20. Auth Dependency Chain

Protected routes declare `current_user: UserResponse = Depends(get_current_user)`. FastAPI executes this entire chain before the handler runs.

### The three functions in `app/dependencies/auth.py`

---

**`create_access_token(data, expires_delta?)`**
- **Accepts:** a dict (should be `{"sub": user_id}`), optional timedelta override
- **What it does:** copies the dict, adds an `exp` claim set to `now + ACCESS_TOKEN_EXPIRE_MINUTES`, then calls `jwt.encode()` with `settings.secret_key` and `settings.algorithm` (HS256)
- **Returns:** a signed JWT string (starts with `eyJ...`)
- **Called by:** register and login route handlers after a successful auth event

---

**`decode_access_token(token)`**
- **Accepts:** raw JWT string extracted from the `Authorization` header
- **What it does:** calls `jwt.decode()` with `settings.secret_key` and `[settings.algorithm]`. This simultaneously verifies the signature and checks the `exp` claim. Extracts `payload["sub"]` as the user ID.
- **Returns:** a `TokenData(user_id=...)` object on success, or `None` on any failure — expired token, tampered signature, malformed token, or missing `sub` claim
- **Called by:** `get_current_user`

---

**`get_current_user(token)`** ← the main dependency
- **Receives:** `token` string via `Depends(oauth2_scheme)`, which reads the `Authorization: Bearer <token>` header. If the header is missing entirely, `oauth2_scheme` raises `401` automatically before `get_current_user` even runs.
- **Step 1:** calls `decode_access_token(token)` → gets `TokenData` or `None`. If `None` → raises `401 "Could not validate credentials"`.
- **Step 2:** calls `get_user_by_id(supabase, token_data.user_id)` → queries `profiles`. If `None` (user deleted since token was issued) → raises `401`.
- **Step 3:** unpacks the profile dict into `UserResponse(**user)`.
- **Returns:** a fully typed `UserResponse` object. This is what the route handler receives as `current_user`.
- **On any failure:** raises `401` with `WWW-Authenticate: Bearer` header. The route handler never runs.

### Full auth flow diagram

```
Client sends: Authorization: Bearer eyJhbGci...

oauth2_scheme
    → extracts raw token string from header (or raises 401 if header missing)

decode_access_token(token)
    → jwt.decode() verifies signature + expiry
    → extracts user_id from payload["sub"]
    → returns TokenData(user_id="abc-123") or None

get_user_by_id(supabase, user_id)
    → SELECT * FROM profiles WHERE id = "abc-123"
    → returns profile dict or None

UserResponse(**profile_dict)
    → Pydantic validates and types the dict
    → returns UserResponse(id=..., username=..., email=..., created_at=...)

Route handler runs with current_user = UserResponse(...)
```

---

## 21. Route Walkthroughs — Every Endpoint

---

### POST /auth/register
**In:** JSON `{ username, email, password }` → **Out:** `{ access_token, token_type }` · HTTP 201

1. FastAPI validates the body against `UserCreate`. Invalid fields → `422` auto-raised, handler never runs.
2. `get_user_by_email(supabase_admin, email)` — queries `profiles`. Returns a dict or `None`. If dict → `400 "An account with this email already exists"`.
3. `supabase_admin.auth.sign_up({email, password})` — Supabase creates the row in `auth.users` and hashes the password. Returns an auth response. If Supabase raises `AuthApiError` → `400`. If `auth_response.user` is falsy → `500`.
4. `create_user_profile(supabase_admin, user_id, username, email)` — inserts a row into `public.profiles`. Admin client used because no JWT session exists yet. Returns the new profile dict (unused here).
5. `create_access_token({"sub": user_id})` — signs a JWT with the user's UUID as the `sub` claim. Returns a JWT string.
6. Returns `Token(access_token=jwt_string)` → serialized as `{ "access_token": "eyJ...", "token_type": "bearer" }`.

---

### POST /auth/login
**In:** Form data `username=email&password=...` → **Out:** `{ access_token, token_type }` · HTTP 200

> Expects **form data**, not JSON. The OAuth2 spec names the field `username` — we use it for the email.

1. `OAuth2PasswordRequestForm` dependency reads `form_data.username` (the email) and `form_data.password` from the form body.
2. `supabase.auth.sign_in_with_password({email: form_data.username, password})` — Supabase looks up `auth.users` and verifies the bcrypt hash internally. If wrong credentials → `AuthApiError` is caught → `401 "Invalid email or password"`.
3. `create_access_token({"sub": user_id})` — same as registration. Returns JWT string.
4. Returns `Token(access_token=jwt_string)`.

---

### GET /auth/me
**In:** Bearer token → **Out:** `{ id, username, email, created_at }` · HTTP 200

1. Auth dependency chain runs (see Section 19) → `current_user: UserResponse`.
2. Handler immediately returns `current_user` — no additional DB call, the user is already loaded.
3. FastAPI serializes `UserResponse` to JSON and sends HTTP 200.

---

### GET /blogs/
**In:** Query params `?skip=0&limit=20` → **Out:** JSON array of blog objects · HTTP 200 · Public

1. FastAPI reads `skip` (default 0) and `limit` (default 20) from the query string.
2. `crud_blog.get_blogs(supabase, skip=skip, limit=limit)` builds a query:
   - Selects `*, profiles(username)` — the join pulls the author's username inline
   - Filters `published = true`
   - Orders `created_at DESC`
   - Paginates via `.range(skip, skip + limit - 1)`
3. Returns a list of blog dicts. FastAPI validates each against `BlogResponse` and serializes to a JSON array.

---

### GET /blogs/me
**In:** Bearer token → **Out:** JSON array of the user's own blogs (including drafts) · HTTP 200

> Route ordering matters: `/me` is registered **before** `/{blog_id}` so FastAPI doesn't treat the literal string `"me"` as a blog ID.

1. Auth dependency chain runs → `current_user`.
2. `crud_blog.get_blogs_by_author(supabase, author_id=str(current_user.id))` — queries `blogs WHERE author_id = current_user.id`, no `published` filter, so drafts are included.
3. Returns list → serialized to JSON array.

---

### GET /blogs/{blog_id}
**In:** Path param `blog_id` → **Out:** single blog object · HTTP 200 · Public

1. `crud_blog.get_blog(supabase, blog_id)` — `SELECT * FROM blogs WHERE id = blog_id`. Returns a dict or `None`.
2. If `None` → `404 "Blog with id '...' not found"`.
3. If found → validated against `BlogResponse`, serialized, sent as HTTP 200.

---

### POST /blogs/
**In:** Bearer token + JSON `{ title, body, published }` → **Out:** created blog object · HTTP 201

1. Auth dependency chain runs → `current_user`.
2. FastAPI validates body against `BlogCreate` (title 5–200 chars, body 10+ chars). Invalid → `422`.
3. `crud_blog.create_blog(supabase, blog=blog, author_id=str(current_user.id))`:
   - Calls `blog.model_dump()` → `{title, body, published}`
   - Merges in `author_id` from the JWT — never from the request body, which prevents impersonation
   - `INSERT INTO blogs ...` → returns the new row dict
4. Returns dict → validated against `BlogResponse`, sent as HTTP 201.

---

### PATCH /blogs/{blog_id}
**In:** Bearer token + JSON with any subset of `{ title?, body?, published? }` → **Out:** updated blog object · HTTP 200

All body fields are optional — only send what you want to change.

1. Auth dependency chain runs → `current_user`.
2. FastAPI validates body against `BlogUpdate` (all fields `Optional`).
3. `crud_blog.get_blog(supabase, blog_id)` — fetch existing record. If `None` → `404 "Blog not found"`.
4. Ownership check: if `existing["author_id"] != current_user.id` → `403 "You are not the author of this blog"`.
5. `crud_blog.update_blog(supabase, blog_id=blog_id, blog=blog)`:
   - `blog.model_dump(exclude_none=True)` strips fields that weren't sent, so only changed fields hit the DB
   - `UPDATE blogs SET ... WHERE id = blog_id` → returns updated row dict
6. Returns dict → validated against `BlogResponse`, sent as HTTP 200.

---

### DELETE /blogs/{blog_id}
**In:** Bearer token + path param → **Out:** empty body · HTTP 204

1. Auth dependency chain runs → `current_user`.
2. `crud_blog.get_blog(supabase, blog_id)` — same fetch as above. If `None` → `404`.
3. Ownership check: if mismatch → `403`.
4. `crud_blog.delete_blog(supabase, blog_id)` — `DELETE FROM blogs WHERE id = blog_id`. Return value ignored here (ownership check already confirmed existence).
5. Handler returns nothing. `status_code=204` sends an empty response body.

---

### GET /users/{user_id}
**In:** Path param `user_id` → **Out:** user profile · HTTP 200 · Public

1. `get_user_by_id(supabase, user_id)` — `SELECT * FROM profiles WHERE id = user_id`. Returns dict or `None`.
2. If `None` → `404 "User with id '...' not found"`.
3. Dict → validated against `UserResponse` (no password field), sent as HTTP 200.

---

## 22. App Startup & Wiring

### What happens when you run `uvicorn app.main:app`

1. Python imports `app/main.py`
2. `main.py` imports the three routers → each router imports its dependencies → this triggers:
   - `app/config.py` — reads `.env`, creates the `settings` singleton. **If any required variable is missing, the app crashes here with a clear error and never starts.**
   - `app/database.py` — creates two Supabase clients using `settings`: `supabase` (respects RLS) and `supabase_admin` (bypasses RLS)
   - `app/models/blog.py` and `app/models/user.py` — Pydantic schema classes are defined
   - `app/dependencies/auth.py` — the `oauth2_scheme` instance is created, JWT functions are defined
3. FastAPI registers all routes from the three `app.include_router(...)` calls
4. Uvicorn starts listening on port 8000

### What `app/main.py` configures

- Creates the `FastAPI()` instance with a title, description, version, and doc URLs (`/docs` for Swagger UI, `/redoc` for ReDoc)
- Adds `CORSMiddleware` — specifies which frontend origins can call the API, whether credentials (cookies/tokens) are allowed, and which methods and headers are permitted. In production replace the wildcard origin with your real frontend domain.
- Adds `RequestLoggingMiddleware` — logs every incoming request (method + path) and the corresponding response (status code + duration in ms) to stdout via Python's `logging` module.
- Registers all three routers: `auth.router` (prefix `/auth`), `blogs.router` (prefix `/blogs`), `users.router` (prefix `/users`)
- Adds a public `GET /` health check endpoint that returns `{"status": "ok"}`

---

## 23. Running, Testing & Debugging

### Start the development server

```bash
# From the blog_api/ directory
uvicorn app.main:app --reload
```

- **API root:** http://localhost:8000
- **Interactive docs (Swagger UI):** http://localhost:8000/docs
- **Reference docs (ReDoc):** http://localhost:8000/redoc

### Testing with Swagger UI

1. Open `/docs`
2. Click `POST /auth/register` → **Try it out** → fill in the body → **Execute**
3. Copy the `access_token` from the response
4. Click **Authorize** (padlock icon, top right) → paste the token → **Authorize**
5. All protected routes now automatically include the `Bearer` token

### Testing with curl

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com", "password": "secret123"}'

# Login (form data — not JSON)
curl -X POST http://localhost:8000/auth/login \
  -d "username=alice@example.com&password=secret123"

# Store token (bash/zsh)
TOKEN="eyJ..."

# Create a blog
curl -X POST http://localhost:8000/blogs/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "My First Post", "body": "This is the body of my blog post."}'

# Get all published blogs (public)
curl http://localhost:8000/blogs/

# Get your own blogs including drafts
curl http://localhost:8000/blogs/me \
  -H "Authorization: Bearer $TOKEN"

# Update a blog (only changed fields needed)
curl -X PATCH http://localhost:8000/blogs/{blog_id} \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'

# Delete a blog
curl -X DELETE http://localhost:8000/blogs/{blog_id} \
  -H "Authorization: Bearer $TOKEN"
```

### VS Code debugger setup

Create `.vscode/launch.json` in `blog_api/`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload"],
      "jinja": true,
      "justMyCode": true
    }
  ]
}
```

Set breakpoints in any route handler. The debugger will pause there on the next matching request.

---

## 24. Error Reference

### Per-endpoint errors

| Endpoint | What went wrong | Response |
|---|---|---|
| Any | Invalid request body field | `422` — detail names the exact field |
| `POST /auth/register` | Email already in profiles table | `400` |
| `POST /auth/register` | Supabase Auth rejected the sign_up | `400` |
| `POST /auth/login` | Wrong email or password | `401` |
| Any protected route | No `Authorization` header | `401` (raised by `oauth2_scheme`) |
| Any protected route | Token expired, tampered, or malformed | `401` |
| Any protected route | User deleted since token was issued | `401` |
| `GET /blogs/{id}` | Blog UUID doesn't exist | `404` |
| `PATCH /blogs/{id}` | Blog UUID doesn't exist | `404` |
| `PATCH /blogs/{id}` | Authenticated but not the author | `403` |
| `DELETE /blogs/{id}` | Blog UUID doesn't exist | `404` |
| `DELETE /blogs/{id}` | Authenticated but not the author | `403` |
| `GET /users/{id}` | User UUID doesn't exist | `404` |
| Any | Supabase / network error | `500` (uncaught) |

### Common startup / development errors

| Error message | Cause | Fix |
|---|---|---|
| `ValidationError` on `Settings` load | Required `.env` variable missing | Add the missing variable — `pydantic-settings` names it exactly |
| `"relation does not exist"` | Table not yet created in Supabase | Run the `CREATE TABLE` SQL in Supabase SQL Editor |
| `ImportError` on startup | Circular import or typo in import path | Read the traceback — it shows the exact file and line |
| Supabase `400` on a write | RLS policy blocking the operation | Use `supabase_admin` for the call or add the correct RLS policy |
| `422 Unprocessable Entity` | Pydantic validation failed on input | Read `detail` — it names the exact field and rule that failed |
| `401 Unauthorized` at runtime | No token, expired token, or wrong secret | Re-login to get a fresh token; verify `SECRET_KEY` in `.env` |
| `403 Forbidden` | Valid token but wrong owner | Check `author_id` vs `current_user.id` in the ownership comparison |
| `404 Not Found` | Record doesn't exist in DB | Verify the UUID is correct |

---

*FastAPI 0.110+ · Pydantic v2 · Supabase Python SDK v2*
