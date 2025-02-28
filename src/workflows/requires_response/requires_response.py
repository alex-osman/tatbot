from agents.tattoo_booking_agent.types import TattooBookingAgentOverallState
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


class Response(BaseModel):
    requires_response: bool = Field(description="Whether the tattoo artist should respond to the email")

def should_respond_to_email(state: TattooBookingAgentOverallState) -> TattooBookingAgentOverallState:
    llm = ChatAnthropic(
        model_name="claude-3-5-sonnet-20240620",
        temperature=0,
        timeout=10,
        stop=None,
    )
    structured_llm = llm.with_structured_output(Response, strict=True, method="json_mode")

    prompt_template = ChatPromptTemplate(
        input_variables=["email_content"],
        messages=[
            ("system", "You are the helpful booking assistant for Know Dice, an up and coming female tattoo artist in Philadelphia.  You are in charge of maintaining the schedule, confirming appointments, and booking new appointments.  Analyze the email thread to extract structured information, including participants, timeline, key messages, actions, context, and final outcome.  Determine if a response is required based on explicit requests or unresolved issues, and return the output in the structured format defined by the Response model."),
            ("human", "{email_content}"),
        ],
    )

    chain = prompt_template | structured_llm

    raw_response = chain.invoke({
        "email_content": state.email["body"],
    })
    response = Response.model_validate(raw_response)

    if response.requires_response:
        return TattooBookingAgentOverallState(
            email=state.email,
            requires_response=True,
            extracted_dates=state.extracted_dates,
            extracted_notes=state.extracted_notes,
            extracted_intent=state.extracted_intent,
            booking_date_start=state.booking_date_start,
            booking_hours_start=state.booking_hours_start,
            gcal_appointments=state.gcal_appointments,
            duration_hours=state.duration_hours,
            response=state.response,
        )
    else:
        return TattooBookingAgentOverallState(
            email=state.email,
            requires_response=False,
            extracted_dates=state.extracted_dates,
            extracted_notes=state.extracted_notes,
            extracted_intent=state.extracted_intent,
            booking_date_start=state.booking_date_start,
            booking_hours_start=state.booking_hours_start,
            gcal_appointments=state.gcal_appointments,
            duration_hours=state.duration_hours,
            response=state.response,
        )
