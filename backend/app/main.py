from fastapi import FastAPI
from .database import engine
from . import models
from .routers import auth, crimes  # Import your route modules

# Bind database generation triggers
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="National Incident & Crime Registry")

# Attach structural API routes
app.include_router(auth.router)
app.include_router(crimes.router)

@app.get("/")
def root():
    return {"status": "System Online", "infrastructure": "Secure Core Matrix Ready"}