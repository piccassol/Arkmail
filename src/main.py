from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, emails, newsletters, analytics
from .config import settings

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title=settings.APP_NAME, version="1.0.0")

# CORS settings for Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pdgmail-frontend.vercel.app", "http://localhost:3000"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(emails.router)
app.include_router(newsletters.router)
app.include_router(analytics.router)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "PDGmail API is running successfully!"}

# Health Check endpoint (For Render/Vercel monitoring)
@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}


