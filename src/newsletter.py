# scheduled_newsletter.py
from utils import generate_email, create_and_send_campaign

def main():
    topic = "What's New?!"
    content = generate_email(f"Compose a weekly newsletter about {topic}")
    create_and_send_campaign(topic, content)

if __name__ == "__main__":
    main()
