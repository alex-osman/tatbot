from datetime import datetime, timedelta

import pytz
from langgraph.graph import END, START, StateGraph
from langsmith import traceable
from pydantic import ValidationError

from _config import *  # noqa: F403
from agents.inbox_agent.types import InboxAgentOverallState
from clients.gmail_search_client import GmailSearch
from workflows.sign_email.sign_email import sign_email
from workflows.draft_response.draft_response import draft_response
from workflows.draft_response.verify_response import verify_response
from workflows.requires_response.requires_response import should_respond_to_email
from workflows.send_email.send_email import send_email

class InboxAgent:
    def __init__(self):
        self.eastern = pytz.timezone("US/Eastern")
        self.client = GmailSearch()
        self.emails = self.client.search_emails(
            query=f"after:{(datetime.now(self.eastern) - timedelta(days=1)).strftime('%Y-%m-%d')}",
            max_results=10,
        )

    @traceable()
    def run(self):
        workflow = StateGraph(InboxAgentOverallState)

        workflow.add_node("should_respond", should_respond_to_email)
        workflow.add_node("draft_response", draft_response)
        workflow.add_node("verify_response", verify_response)
        workflow.add_node("sign_email", sign_email)
        workflow.add_node("send_email", send_email)

        workflow.add_edge(START, "should_respond")

        def should_respond_logic(state: InboxAgentOverallState):
            if state.requires_response:
                return "draft_response"
            else:
                return END

        def verify_response_logic(state: InboxAgentOverallState):
            if state.valid_response:
                return "sign_email"
            else:
                return "draft_response"

        workflow.add_conditional_edges("should_respond", should_respond_logic)
        workflow.add_edge("draft_response", "verify_response")
        workflow.add_conditional_edges("verify_response", verify_response_logic)
        workflow.add_edge("verify_response", "sign_email")
        workflow.add_edge("sign_email", "send_email")
        graph = workflow.compile()

        print(self.emails[0]["subject"])
        
        result = graph.invoke({
            "email_subject": self.emails[0]["subject"],
            "email_content": self.emails[0]["body"],
        })

        try:
            return InboxAgentOverallState(**result)
        except ValidationError as e:
            raise TypeError(f"Result is not valid: {e}")
