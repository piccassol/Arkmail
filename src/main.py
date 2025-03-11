from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.database import engine, Base
from src.routers import auth, emails, newsletters, analytics
from src.config import settings  # Ensure `config.py` is inside `src/`

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

# CORS settings for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(emails.router)
app.include_router(newsletters.router)
app.include_router(analytics.router)

@app.get("/")
def read_root():
    return {"message": "PDGmail API Running"}
