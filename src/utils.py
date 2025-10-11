# src/utils.py
import os
from mailchimp_marketing import Client
from resend import Resend
import requests
from dotenv import load_dotenv

load_dotenv()

# Configure Resend client
resend = Resend(api_key=os.getenv("RESEND_API_KEY"))

# Configure Mailchimp client
mailchimp = Client()
mailchimp.set_config({
    "api_key": os.getenv("MAILCHIMP_API_KEY"),
    "server": os.getenv("MAILCHIMP_SERVER_PREFIX")
})

def generate_email(prompt: str) -> str:
    """Generate an email using Ollama's GPT-20 OSS model."""
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "gpt-20-oss",  # Replace with actual model name if different (e.g., 'llama3')
                "messages": [
                    {"role": "system", "content": "You are a professional email assistant."},
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    except requests.RequestException as e:
        raise Exception(f"Failed to generate email with Ollama: {str(e)}")

def send_email(to: str, subject: str, html: str) -> dict:
    """Send an email using Resend."""
    try:
        response = resend.emails.send({
            "from": "your@domain.com",  # Replace with your verified Resend sender email
            "to": to,
            "subject": subject,
            "html": html
        })
        return {"status": "success", "data": response}
    except Exception as e:
        raise Exception(f"Failed to send email with Resend: {str(e)}")

def create_and_send_campaign(subject: str, content_html: str) -> dict:
    """Create and send a Mailchimp campaign."""
    try:
        campaign = mailchimp.campaigns.create({
            "type": "regular",
            "recipients": {"list_id": os.getenv("MAILCHIMP_LIST_ID")},
            "settings": {
                "subject_line": subject,
                "from_name": "Your Business Name",
                "reply_to": "youremail@example.com"
            }
        })
        mailchimp.campaigns.set_content(campaign["id"], {"html": content_html})
        mailchimp.campaigns.send(campaign["id"])
        return {"status": "success", "campaign_id": campaign["id"]}
    except Exception as e:
        raise Exception(f"Failed to create/send Mailchimp campaign: {str(e)}")

def get_mailchimp_lists() -> dict:
    """Fetch all Mailchimp lists."""
    try:
        response = mailchimp.lists.get_all_lists()
        return response
    except Exception as e:
        raise Exception(f"Failed to fetch Mailchimp lists: {str(e)}")

def get_mailchimp_stats() -> dict:
    """Fetch Mailchimp campaign stats."""
    try:
        response = mailchimp.reports.get_all_campaign_reports()
        return response
    except Exception as e:
        raise Exception(f"Failed to fetch Mailchimp stats: {str(e)}")