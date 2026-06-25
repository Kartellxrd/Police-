from fastapi import FastAPI
from .database import engine
from . import models
from .routers import auth, crimes, dashboard,suspects  # Import your route modules

# Bind database generation triggers
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="National Incident & Crime Registry")

# Attach structural API routes
app.include_router(auth.router)
app.include_router(crimes.router)
app.include_router(dashboard.router)
app.include_router(suspects.router)


@app.get("/")
def root():
    return {"status": "System Online"}