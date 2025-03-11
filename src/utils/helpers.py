import random
import string

def generate_random_string(length=12):
    """Generate a random string of fixed length."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def format_email_preview(body: str, max_length=100):
    """Format the email preview to a fixed length."""
    return body[:max_length] + "..." if len(body) > max_length else body
