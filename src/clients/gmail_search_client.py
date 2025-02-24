import base64
import email
from enum import Enum
from typing import Any

from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from clients.log import Log

logger = Log(__name__)

class Resource(str, Enum):
    """Enumerator of Resources to search."""

    THREADS = "threads"
    MESSAGES = "messages"

def clean_email_body(body: str) -> str:
    """Clean email body."""
    try:
        try:
            soup = BeautifulSoup(str(body), "html.parser")
            body = soup.get_text()
            return str(body)
        except Exception as e:
            logger.exception(e)
            return str(body)
    except ImportError:
        logger.warning("BeautifulSoup not installed. Skipping cleaning.")
        return str(body)

DEFAULT_TOKEN_FILE = "token.json"

class GmailSearch:
    def __init__(self, token_file: str = DEFAULT_TOKEN_FILE) -> None:
        self.credentials = Credentials.from_authorized_user_file(
            token_file, scopes=["https://mail.google.com/"]
        )
        self.api_resource = build("gmail", "v1", credentials=self.credentials)

    def _parse_threads(self, threads: list[dict[str, Any]]) -> list[dict[str, Any]]:
        results = []
        for thread in threads:
            thread_id = thread["id"]
            thread_data = (
                self.api_resource.users()
                .threads()
                .get(userId="me", id=thread_id)
                .execute()
            )
            messages = thread_data["messages"]
            thread["messages"] = []
            for message in messages:
                snippet = message["snippet"]
                thread["messages"].append({"snippet": snippet, "id": message["id"]})
            results.append(thread)

        return results

    def _parse_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        results = []
        for message in messages:
            message_id = message["id"]
            message_data = (
                self.api_resource.users()
                .messages()
                .get(userId="me", format="raw", id=message_id)
                .execute()
            )

            raw_message = base64.urlsafe_b64decode(message_data["raw"])

            email_msg = email.message_from_bytes(raw_message)

            subject = email_msg["Subject"]
            sender = email_msg["From"]

            message_body = ""
            if email_msg.is_multipart():
                for part in email_msg.walk():
                    ctype = part.get_content_type()
                    cdispo = str(part.get("Content-Disposition"))
                    if ctype == "text/plain" and "attachment" not in cdispo:
                        try:
                            message_body = part.get_payload(decode=True).decode("utf-8")  # type: ignore[union-attr]
                        except UnicodeDecodeError:
                            message_body = part.get_payload(decode=True).decode(  # type: ignore[union-attr]
                                "latin-1"
                            )
                        break
            else:
                message_body = email_msg.get_payload(decode=True).decode("utf-8")  # type: ignore[union-attr]

            body = clean_email_body(message_body)

            results.append(
                {
                    "id": message["id"],
                    "threadId": message_data["threadId"],
                    "snippet": message_data["snippet"],
                    "body": body,
                    "subject": subject,
                    "sender": sender,
                    "from": email_msg["From"],
                    "date": email_msg["Date"],
                    "to": email_msg["To"],
                    "cc": email_msg["Cc"],
                }
            )
        return results

    def search_emails(
        self,
        query: str,
        resource: Resource = Resource.MESSAGES,
        max_results: int = 10,
    ) -> list[dict[str, Any]]:
        results = (
            self.api_resource.users()
            .messages()
            .list(userId="me", q=query, maxResults=max_results)
            .execute()
            .get(resource.value, [])
        )
        if resource == Resource.THREADS:
            return self._parse_threads(results)
        elif resource == Resource.MESSAGES:
            return self._parse_messages(results)
        else:
            raise NotImplementedError(f"Resource of type {resource} not implemented.")
