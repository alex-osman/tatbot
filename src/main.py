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
    print(results)
