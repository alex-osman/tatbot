from pydantic import BaseModel

from _config import *  # noqa: F403
from agents.inbox_agent.inbox_agent import InboxAgent


class MessagesState(BaseModel):
    email_content: str
    is_valid_response: bool
    response: str

if __name__ == "__main__":
    draft_responses_agent = InboxAgent()
    results = draft_responses_agent.run()

    # Print that you started with this email:
    print(f"Started with this email: \n{results.email_content}")

    # Print that you signed this email:
    print(f"Signed this email: \n{results.signed_email}")

    # Print that you sent this email:
    print(f"Sent this email.")
