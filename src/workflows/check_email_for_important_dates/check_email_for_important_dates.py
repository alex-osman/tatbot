import datetime
from typing import List, Optional
from agents.tattoo_booking_agent.types import BookingIntent, TattooBookingAgentOverallState
from clients.gcal_search_client import GCalSearch
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

class Response(BaseModel):
    action: BookingIntent  # BOOK_DATE, FIND_DATE, RESCHEDULE, CANCEL, or NONE
    dates: Optional[List[str]]  # List of extracted dates (ISO format)
    notes: Optional[str]  # Extra details like preferred time
    duration_hours: Optional[int] = None  # Extracted session length in hours
    booking_date_start: Optional[str] = None  # Extracted start date of the booking session (ISO format)
    booking_hours_start: Optional[str] = None  # Extracted start time of the booking session (HH:MM)

def prepare_to_book_session(state: TattooBookingAgentOverallState) -> TattooBookingAgentOverallState:
    llm = ChatAnthropic(
        model_name="claude-3-5-sonnet-20240620",
        temperature=0.2,
        timeout=10,
        stop=None,
    )
    
    structured_llm = llm.with_structured_output(Response)

    prompt_template = ChatPromptTemplate(
    [
        ("system", "You are a helpful tattoo booking assistant for Know Dice, a Philadelphia-based tattoo artist."),
        ("human", """
            Here is the email from {email_from}:
            Subject: {email_subject}
            Body: {email_content}

            Extract the following **as structured JSON**:
            - **Booking Date Start**: The start date of the booking session (ISO format YYYY-MM-DD)
            - **Booking Hours Start**: The start time of the booking session (HH:MM)
            - **Calendar Title**: The title of the calendar event (e.g. "Tat: John Doe - Angel")
            - **Calendar Description**: The description of the calendar event (e.g. "Angel on the left shoulder, hand poke")
            Return only valid JSON with this structure:
            {{
                "booking_date_start": "<ISO format YYYY-MM-DD>",
                "booking_hours_start": "<HH:MM>",
                "calendar_title": "<Title of the calendar event>",
                "calendar_description": "<Description of the calendar event>",
            }}
        """),
    ]
    )

    chain = prompt_template | structured_llm

    raw_response = chain.invoke({
        "email_from": state.email["from"],
        "email_subject": state.email["subject"],
        "email_content": state.email["body"],
    })
    response = Response.model_validate(raw_response)
    
    # Create a calendar event
    gcal_client = GCalSearch()
    gcal_client.book_appointment(response.calendar_title, response.calendar_description, response.booking_date_start, response.booking_hours_start, state.duration_hours)
    return TattooBookingAgentOverallState(
        email=state.email,
        duration_hours=state.duration_hours,
        booking_date_start=response.booking_date_start,
        booking_hours_start=response.booking_hours_start,
        calendar_title=response.calendar_title,
        calendar_description=response.calendar_description,
    )
    

def extract_info_from_email(state: TattooBookingAgentOverallState) -> TattooBookingAgentOverallState:
    llm = ChatAnthropic(
        model_name="claude-3-5-sonnet-20240620",
        temperature=0.2,
        timeout=10,
        stop=None,
    )
    structured_llm = llm.with_structured_output(Response)

    prompt_template = ChatPromptTemplate(
    [
        ("system", "You are a helpful tattoo booking assistant for Know Dice, a Philadelphia-based tattoo artist."),
        ("human", """
            Here is the email from {email_from}:
            Subject: {email_subject}
            Body: {email_content}

            Extract the following **as structured JSON**:
            - **Intent**: One of ["book_date", "find_date", "reschedule", "cancel", "none"]
            - **Dates**: A list of dates mentioned (ISO format YYYY-MM-DD). Remember that today is {today_date}.
            - **Duration**: Estimated session length in hours (integer or null if unclear)
            - **Notes**: Additional relevant details (e.g., 'wants an afternoon session')
            - **Booking Date Start**: The start date and time of the booking session (ISO format YYYY-MM-DD)
            - **Booking Hours Start**: The start time of the booking session (HH:MM)


            Return only valid JSON with this structure:
            {{
                "action": "<Intent>",
                "dates": ["YYYY-MM-DD", "YYYY-MM-DD"],
                "duration_hours": <Integer or None>,
                "notes": "<Additional info>",
                "booking_date_start": "<ISO format YYYY-MM-DD>",
                "booking_hours_start": "<HH:MM>",
            }}
        """),
    ]
)


    chain = prompt_template | structured_llm

    raw_response = chain.invoke({
        "email_from": state.email["from"],
        "email_subject": state.email["subject"],
        "email_content": state.email["body"],
        "today_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
    })
    response = Response.model_validate(raw_response)

    return TattooBookingAgentOverallState(
        email=state.email,
        extracted_dates=response.dates,
        extracted_notes=response.notes,
        extracted_intent=response.action,
        duration_hours=response.duration_hours,
        booking_date_start=response.booking_date_start,
        booking_hours_start=response.booking_hours_start,
    )