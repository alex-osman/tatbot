import base64
from email.message import EmailMessage
from typing import Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from clients.log import Log

logger = Log(__name__)

DEFAULT_TOKEN_FILE = "token.json"

class GmailReply:
    def __init__(self, token_file: str = DEFAULT_TOKEN_FILE) -> None:
        self.credentials = Credentials.from_authorized_user_file(
            token_file, scopes=["https://mail.google.com/"]
        )
        self.api_resource = build("gmail", "v1", credentials=self.credentials)

    def reply_to_email(self, email: dict[str, Any], content: str) -> None:
        print(f"Replying to {email['subject']} with {content}")
        try:
            message = EmailMessage()
            message.set_content(content)

            # message["To"] = email_from
            message["To"] = "alexosman@live.com"
            message["From"] = "alexosman39@gmail.com"
            message["Subject"] = email['subject']
            message["In-Reply-To"] = email['threadId']
            message["References"] = email['threadId']

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            create_message = {"raw": encoded_message, "threadId": email['threadId']}
            send_message = (
                self.api_resource.users()
                .messages()
                .send(userId="me", body=create_message)
                .execute()
            )
            print(f'Message Id: {send_message["id"]}')

        except Exception as error:
            print(f"An error occurred: {error}")
            raise
