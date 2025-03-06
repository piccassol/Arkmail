# src/utils.py
import openai
import os
from mailchimp_marketing import Client
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_email(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a professional email assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

mailchimp = Client()
mailchimp.set_config({
    "api_key": os.getenv("MAILCHIMP_API_KEY"),
    "server": os.getenv("MAILCHIMP_SERVER_PREFIX")
})

def create_and_send_campaign(subject, content_html):
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
