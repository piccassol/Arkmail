from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, emails, newsletters, analytics
from .config import settings

# Ensure database tables are created
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="PDGmail API")

# CORS settings for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend URL in production
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
    return {"message": "PDGmail API is running on Render"}

# Health check endpoint for deployment debugging
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Backend is live!"}
