from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 1. Imported the CORS middleware module
from .database import engine
from . import models
from .routers import auth, crimes, dashboard, suspects 

# Bind database generation triggers
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="National Incident & Crime Registry")

# 2. Configured and attached CORS settings right below app initialization
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows your frontend Codespace network address to make fetch calls
    allow_credentials=True,
    allow_methods=["*"],  # Allows POST, GET, OPTIONS, etc.
    allow_headers=["*"],  # Allows Authorization headers, Content-Type, etc.
)

# Attach structural API routes
app.include_router(auth.router)
app.include_router(crimes.router)
app.include_router(dashboard.router)
app.include_router(suspects.router)


@app.get("/")
def root():
    return {"status": "System Online"}