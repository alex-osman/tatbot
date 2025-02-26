from pydantic import BaseModel

from agents.inbox_agent.types import InboxAgentOverallState
from clients.gmail_reply_client import GmailReply

def send_email(state: InboxAgentOverallState) -> InboxAgentOverallState:
    print(f"Sending email from {state.email_from}")
    gmail_reply = GmailReply()
    gmail_reply.reply_to_email(state.email_from, state.email_subject, state.signed_email)

    return InboxAgentOverallState(
        email_content=state.email_content,
        email_subject=state.email_subject,
        email_from=state.email_from,
        requires_response=state.requires_response,
        response=state.response,
        signed_email=state.signed_email,
    )   
