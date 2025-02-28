from datetime import datetime, timedelta
from typing import List

import pytz
from clients.gcal_search_client import GCalSearch
from langgraph.graph import END, START, StateGraph
from langsmith import traceable
from pydantic import ValidationError

from _config import *  # noqa: F403
from agents.tattoo_booking_agent.types import TattooBookingAgentOverallState, BookingIntent
from clients.gmail_search_client import GmailSearch
from workflows.draft_response.draft_response import draft_response
from workflows.draft_response.verify_response import verify_response
from workflows.requires_response.requires_response import should_respond_to_email
from workflows.send_email.send_email import send_email
from workflows.check_email_for_important_dates.check_email_for_important_dates import extract_info_from_email, prepare_to_book_session

class TattooBookingAgent:
    def __init__(self):
        self.eastern = pytz.timezone("US/Eastern")
        self.client = GmailSearch()
        self.emails = self.client.search_emails(
            query=f"after:{(datetime.now(self.eastern) - timedelta(days=1)).strftime('%Y-%m-%d')}",
            max_results=10,
        )
        
        self.gcal_client = GCalSearch()
        
    def get_gcal_appointments(self, state: TattooBookingAgentOverallState):
        print("Getting GCal appointments for dates: ", state.extracted_dates)
        appointments = []
        for date in state.extracted_dates:
            appointments.extend(self.gcal_client.get_appointments_for_date(date))
        state.gcal_appointments = appointments
        print("GCal appointments: ", len(state.gcal_appointments))
        return state
    
    def book_session(self, state: TattooBookingAgentOverallState):
        print("Booking session for dates: ", state.extracted_dates)
        print("Booking session for dates: ", state.booking_date_start, state.booking_hours_start, state.duration_hours)
        self.gcal_client.book_appointment(state.email["from"], state.email["subject"], state.booking_date_start, state.booking_hours_start, state.duration_hours or 3)
        return state

    @traceable()
    def run(self):
        workflow = StateGraph(TattooBookingAgentOverallState)

        workflow.add_node("respond_to_email", should_respond_to_email)
        workflow.add_node("extract_info_from_email", extract_info_from_email)
        workflow.add_node("get_gcal_appointments", self.get_gcal_appointments)
        workflow.add_node("prepare_to_book_session", prepare_to_book_session)
        workflow.add_node("book_session", self.book_session)
        workflow.add_node("draft_response", draft_response)
        # workflow.add_node("send_email", send_email)
        

        def should_respond_logic(state: TattooBookingAgentOverallState):
            if state.requires_response:
                print("Responding to email", state.email["subject"])
                return "extract_info_from_email"
            else:
                print("Not responding to email", state.email["subject"])
                return END    
        

        def extract_info_logic(state: TattooBookingAgentOverallState):
            if state.extracted_intent == BookingIntent.FIND_DATE:
                return "get_gcal_appointments"
            elif state.extracted_intent == BookingIntent.BOOK_DATE:
                return "book_session"
            else:
                return END

        workflow.add_edge(START, "respond_to_email")
        workflow.add_conditional_edges("respond_to_email", should_respond_logic)
        workflow.add_conditional_edges("extract_info_from_email", extract_info_logic)
        workflow.add_edge("get_gcal_appointments", "draft_response")
        workflow.add_edge("book_session", "draft_response")
        workflow.add_edge("draft_response", END)
        
        graph = workflow.compile()

        email = self.emails[0]
        print(email)
        result = graph.invoke({
            "email": email,
        })

        try:
            return TattooBookingAgentOverallState(**result)
        except ValidationError as e:
            raise TypeError(f"Result is not valid: {e}")
