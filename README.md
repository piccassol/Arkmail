🚢 AI-Powered Email Automation Agent

This repository contains an automated AI agent integrated with Mailchimp, designed to automate professional business emailing and newsletter management efficiently.

🛠️ Project Setup

Step 1: Clone Repository and Setup

git clone https://github.com/piccassol/email_agent.git
cd email_agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Step 2: Configure Environment

Create a .env file based on .env.example and populate with your API keys:

OPENAI_API_KEY=your_openai_api_key
MAILCHIMP_API_KEY=your_mailchimp_api_key
MAILCHIMP_SERVER_PREFIX=usX
MAILCHIMP_LIST_ID=your_mailchimp_list_id

Step 3: Run the FastAPI Backend

uvicorn src.main:app --reload

Visit http://localhost:8000/docs to interact with your API.

Project Structure

email_agent/
├── src/
│   ├── main.py       # FastAPI application
│   └── utils.py      # AI and Mailchimp utilities
├── venv/             # Python virtual environment
├── .env              # Environment variables (excluded from Git)
├── .gitignore
├── requirements.txt
└── README.md

Automating Email Sending

To automate regular newsletter sending, set up a cron job:

crontab -e

Add the line below (adjusting the path):

0 9 * * 1 /path/to/venv/bin/python /path/to/email_agent/src/main.py

Tech Stack

Backend: FastAPI

AI: OpenAI (GPT-4-turbo)

Email Automation: Mailchimp

Git Workflow

Commit and push your changes clearly:

git add .
git commit -m "🚢 Clear description of changes"
git push origin main

✅ Current Features:

Automated email generation via AI

Mailchimp integration for newsletter automation

FastAPI backend for scalability

🚢 Upcoming Improvements:

CRM Integration

Enhanced personalization using user data

Advanced email analytics and monitoring
