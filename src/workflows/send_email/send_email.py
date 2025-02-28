from pydantic import BaseModel

from agents.tattoo_booking_agent.types import TattooBookingAgentOverallState
from clients.gmail_reply_client import GmailReply

def send_email(state: TattooBookingAgentOverallState) -> TattooBookingAgentOverallState:
    print(f"Sending email from {state.email['from']}")
    gmail_reply = GmailReply()
    gmail_reply.reply_to_email(state.email, state.response)

    return TattooBookingAgentOverallState(
        email=state.email,
        email_sent=True
    )