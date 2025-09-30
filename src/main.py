from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os

app = FastAPI(title="Arkmail - ARK Technologies Email Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmailRequest(BaseModel):
    campaign_type: str
    recipient_data: dict
    client_id: str
    industry: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Arkmail API - ARK Technologies", "version": "1.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "arkmail"}

@app.post("/api/v1/generate-email")
async def generate_email(request: EmailRequest):
    # Placeholder for now - you can add OpenAI integration later
    return {
        "success": True,
        "email_content": f"Email generated for {request.recipient_data.get('name')}",
        "campaign_type": request.campaign_type
    }

@app.get("/api/v1/campaigns")
async def list_campaigns():
    return {"campaigns": [], "message": "Mailchimp integration pending"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8025)
