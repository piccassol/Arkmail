# src/main.py
from fastapi import FastAPI
from utils import generate_email, create_and_send_campaign

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "🚢 AI Email Agent Ready!"}

@app.post("/send-newsletter")
async def send_newsletter(topic: str):
    prompt = f"Compose a professional newsletter about: {topic}"
    newsletter_content = generate_email(prompt)
    create_and_send_campaign(subject=topic, content_html=newsletter_content)
    return {"status": "🚢 Newsletter successfully sent!"}
