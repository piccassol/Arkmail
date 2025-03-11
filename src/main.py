from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base  # Removed "src." to match Render's directory structure
from routers import auth, emails, newsletters, analytics
from config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

# CORS settings for Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific frontend URL in production
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
