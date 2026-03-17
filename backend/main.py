# import os
# from pathlib import Path
# from fastapi import FastAPI,Request
# from fastapi.middleware.cors import CORSMiddleware #cross origin resouse sharing 
# from fastapi.responses import FileResponse,JSONResponse
# from fastapi.staticfiles import StaticFiles
# from dotenv import load_dotenv
# from fastapi.staticfiles import StaticFiles
# load_dotenv

# #calling auth and docs
# from backend.routes.auth_routes import router as auth_router
# from backend.routes.document_routes import router as doc_router


# app=FastAPI(
#     title="GUPTA VAULT",
#     description="DOCUMENT STORAGE",
#     version="1.0.0",
# )
# app.mount("/static", StaticFiles(directory="frontend"), name="static")

# # setting up CORS to help accept all origin  requests
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # allows any website to call API
#     allow_credentials=True,  # make cookies and auth header needed for login sessions
#     allow_methods=["*"], # allow http methods like POST,GET etc
#     allow_headers=["*"],
# )

# #to create endpoints
# app.include_router(auth_router)
# app.include_router(doc_router)


# FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

# @app.get("/")
# async def root():
#     return FileResponse(FRONTEND_DIR / "login.html")

# @app.get("/dashboard")
# async def dashboard():
#     return FileResponse(FRONTEND_DIR / "dashboard.html")

# @app.get("/upload")
# async def upload_page():
#     return FileResponse(FRONTEND_DIR / "upload.html")
# @app.get("/health")
# async def health():
#     return {"status":"ok","service": "GUPTA VAULT"}


# @app.on_event("startup")
# async def startup_event():
#     secure_dir =Path(__file__).parent.parent / "secure_docs"
#     secure_dir.mkdir(exist_ok=True)
#     print(f"GUPTA VAULT Started")
#     print(f"Secure docs directory: {secure_dir}")
#     print(f"Admin: {os.getenv('ADMIN_EMAIL', 'not set')}")

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Routers
from backend.routes.auth_routes import router as auth_router
from backend.routes.document_routes import router as doc_router


# Base directory (ABSOLUTE — important for Linux)
BASE_DIR = Path(__file__).resolve().parent.parent

# Frontend directory
FRONTEND_DIR = BASE_DIR / "frontend"

# Secure docs directory
SECURE_DOCS_DIR = BASE_DIR / "secure_docs"


app = FastAPI(
    title="GUPTA VAULT",
    description="DOCUMENT STORAGE",
    version="1.0.0",
)


# Note: Static files are served via a catch-all route at the bottom of the file
# to handle both nested (css/...) and flat frontend directory structures correctly.


# CORS (keep as is)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(auth_router)
app.include_router(doc_router)


# -------------------------------
# Frontend Routes
# -------------------------------

@app.get("/")
async def root():
    return FileResponse(FRONTEND_DIR / "login.html")


@app.get("/dashboard")
async def dashboard():
    return FileResponse(FRONTEND_DIR / "dashboard.html")


@app.get("/upload")
async def upload_page():
    return FileResponse(FRONTEND_DIR / "upload.html")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "GUPTA VAULT"}


# -------------------------------
# Catch-all Static File Route
# -------------------------------

@app.get("/{file_path:path}")
async def serve_static(file_path: str):
    """
    Catch-all route to serve static files (CSS, JS). Designed to gracefully handle 
    both flat architectures and nested 'css/' or 'js/' folder structures
    no matter what changes are made on the frontend.
    """
    # 1. Try exact path (in case files were structured into css/ and js/ folders)
    full_path = FRONTEND_DIR / file_path
    if full_path.is_file():
        return FileResponse(full_path)
    
    # 2. Fallback to flat filename (in case html asks for /css/login.css but folder is flat)
    filename = Path(file_path).name
    flat_path = FRONTEND_DIR / filename
    if flat_path.is_file():
        return FileResponse(flat_path)

    return JSONResponse(status_code=404, content={"message": "Not Found"})


# -------------------------------
# Startup Event
# -------------------------------

@app.on_event("startup")
async def startup_event():
    SECURE_DOCS_DIR.mkdir(exist_ok=True)

    print("GUPTA VAULT Started")
    print(f"Secure docs directory: {SECURE_DOCS_DIR}")
    print(f"Admin: {os.getenv('ADMIN_EMAIL', 'not set')}")