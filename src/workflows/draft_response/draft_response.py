from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from agents.tattoo_booking_agent.types import TattooBookingAgentOverallState


class Response(BaseModel):
    response: str

def draft_response(state: TattooBookingAgentOverallState) -> TattooBookingAgentOverallState:
    llm = ChatAnthropic(
        model_name="claude-3-5-sonnet-20240620",
        temperature=0.35,
        timeout=10,
        stop=None,
    )
    structured_llm = llm.with_structured_output(Response)

    prompt_template = ChatPromptTemplate(
        [
            ("system", "You are Jennifer (or Jen or Jenny) the assistant of Know Dice, an up and coming female tattoo artist in Philadelphia.  You are in charge of maintaining the schedule, confirming appointments, and booking new appointments.  Analyze the email thread to extract structured information, including participants, timeline, key messages, actions, context, and final outcome.  You are super cool and chill and hip.  Make sure to try and get people to book appointments.  Draft a response to the email based on the information extracted. Keep it concise and make sure to cover pricing, availability/booking, and details about the tattoo such as size, colors, handpoke or machine, and location.  If suggesting a time, make sure to suggest a time that is after 10am and before 6pm.  You may give them a few options and ask them to pick one.  It is preferrable to pack multiple tattoos into one day."),
            ("user", """
                Here is the email from {email_from}:
                Subject: {email_subject}
                Body: {email_content}
                
                
                Here is your availability for the following dates:
                {gcal_appointments}
            """),
        ]
    )

    chain = prompt_template | structured_llm

    raw_response = chain.invoke({
        "email_from": state.email["from"],
        "email_subject": state.email["subject"],
        "email_content": state.email["body"],
        "gcal_appointments": state.gcal_appointments,
    })
    response = Response.model_validate(raw_response)

    return TattooBookingAgentOverallState(
        email=state.email,
        extracted_dates=state.extracted_dates,
        extracted_notes=state.extracted_notes,
        extracted_intent=state.extracted_intent,
        duration_hours=state.duration_hours,
        gcal_appointments=state.gcal_appointments,
        response=response.response,
    )