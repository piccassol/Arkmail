from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os

from database import engine, get_db
from models import user, email, newsletter
from routers import auth, emails, newsletters, analytics

# TEMPORARILY COMMENT OUT TABLE CREATION
# user.Base.metadata.create_all(bind=engine)
# email.Base.metadata.create_all(bind=engine)
# newsletter.Base.metadata.create_all(bind=engine)

# Create FastAPI app instance
app = FastAPI(
    title="ArkMail - ARK Technologies Email Platform",
    version="2.0.0",
    description="Email management and newsletter platform with Resend integration"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mail.arktechnologies.ai",
        "https://arktechnologies.ai",
        "http://localhost:3000",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoints
@app.get("/")
async def root():
    return {
        "message": "ArkMail API - ARK Technologies",
        "version": "2.0.0",
        "status": "operational",
        "features": ["authentication", "email", "newsletters", "analytics"]
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = "disconnected"
        
    return {
        "status": "healthy",
        "service": "arkmail",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "database": db_status
    }

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(emails.router, prefix="/api/emails", tags=["Emails"])
app.include_router(newsletters.router, prefix="/api/newsletters", tags=["Newsletters"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

# Legacy endpoint for backward compatibility
@app.post("/api/v1/generate-email")
async def generate_email_legacy():
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="This endpoint has been deprecated. Please use /api/emails/send instead."
    )

@app.get("/api/v1/campaigns")
async def list_campaigns_legacy():
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="This endpoint has been deprecated. Please use /api/newsletters instead."
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENVIRONMENT") != "production"
    )