import re
from external.gmail.gmail_client import GmailService

email_tool_description =     {
    "name": "send_email",
    "description": "Send an email to a specified recipient",
    "input_schema": {
        "type": "object",
        "properties": {
            "recipient": {"type": "string", "description": "Email recipient"},
            "content": {"type": "string", "description": "Email body"}
        },
        "required": ["recipient", "content"]
    }
}

def parse_and_send_email(input_text):
    pattern = re.compile(
        r'send_email\s*\(\s*recipient\s*=\s*"([^"]+)"\s*,\s*content\s*=\s*"([^"]+)"\s*\)', 
        re.DOTALL
    )
    match = pattern.search(input_text)
    if match:
        recipient = match.group(1)
        content = match.group(2)
        send_email(recipient, content)
        return True, "Email sent successfully"
    else:
        return False, "Email not sent due to missing required parameters"

def send_email(recipient: str, content: str) -> str:
    DEFAULT_SENDER = "ymchen217@gmail.com"
    gmail_service = GmailService()

    message = gmail_service.create_message(
            sender=DEFAULT_SENDER,
            to=recipient,
            subject="Test Email from Christie",
            message_text=content
        )

    gmail_service.send_email(message)

    return f"Email sent to {recipient} with message: {content}"
