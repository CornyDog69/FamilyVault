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
from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware #cross origin resouse sharing 
from fastapi.responses import FileResponse,JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
load_dotenv

#calling auth and docs
from backend.routes.auth_routes import router as auth_router
from backend.routes.document_routes import router as doc_router


app=FastAPI(
    title="GUPTA VAULT",
    description="DOCUMENT STORAGE",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# setting up CORS to help accept all origin  requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allows any website to call API
    allow_credentials=True,  # make cookies and auth header needed for login sessions
    allow_methods=["*"], # allow http methods like POST,GET etc
    allow_headers=["*"],
)

#to create endpoints
app.include_router(auth_router)
app.include_router(doc_router)


FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

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
    return {"status":"ok","service": "GUPTA VAULT"}


@app.on_event("startup")
async def startup_event():
    secure_dir =Path(__file__).parent.parent / "secure_docs"
    secure_dir.mkdir(exist_ok=True)
    print(f"GUPTA VAULT Started")
    print(f"Secure docs directory: {secure_dir}")
    print(f"Admin: {os.getenv('ADMIN_EMAIL', 'not set')}")