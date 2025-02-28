import os
from agents.tattoo_booking_agent.tattoo_booking_agent import TattooBookingAgent
from clients.gcal_search_client import GCalSearch
from pydantic import BaseModel

from _config import *  # noqa: F403


class MessagesState(BaseModel):
    email_content: str
    email_subject: str
    email_from: str
    is_valid_response: bool
    response: str

if __name__ == "__main__":
    tattoo_booking_agent = TattooBookingAgent()
    results = tattoo_booking_agent.run()
    
    print("Done")
