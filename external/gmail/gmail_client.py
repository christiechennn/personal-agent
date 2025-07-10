import os
import pickle
import base64
import logging
from typing import Optional, Dict, Any
from email.message import EmailMessage
from google.auth.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class GmailService:
    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.pickle'):
        """
        Initialize the Gmail service.

        Args:
            credentials_path: Path to the credentials.json file
            token_path: Path to save/load the token pickle file
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.creds = self.load_credentials()
        self.service = self.build_service()

    def load_credentials(self) -> Optional[Credentials]:
        try:
            creds = None
            # Load existing credentials
            if os.path.exists(self.token_path):
                with open(self.token_path, 'rb') as token:
                    creds = pickle.load(token)

            # If no valid credentials available, create new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_path):
                        raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)

                # Save credentials
                with open(self.token_path, 'wb') as token:
                    pickle.dump(creds, token)

            return creds
        except Exception as e:
            logger.error(f"Error loading credentials: {str(e)}")
            raise

    def build_service(self) -> Any:
        try:
            return build('gmail', 'v1', credentials=self.creds)
        except Exception as e:
            logger.error(f"Error building service: {str(e)}")
            raise

    @staticmethod
    def create_message(sender: str, to: str, subject: str, message_text: str) -> Dict[str, str]:
        try:
            message = EmailMessage()
            message.set_content(message_text)
            message['To'] = to
            message['From'] = sender
            message['Subject'] = subject
        
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            return {'raw': raw}
        
        except Exception as e:
            logger.error(f"Error creating message: {str(e)}")
            raise

    def send_email(self, message: Dict[str, str]) -> None:
        try:
            self.service.users().messages().send(userId='me', body=message).execute()
            logger.info("Email sent successfully.")

        except Exception as e:
            logger.error(f"An error occurred while sending the email: {str(e)}")
            raise
