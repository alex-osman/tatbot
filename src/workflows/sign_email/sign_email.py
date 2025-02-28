from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from agents.inbox_agent.types import InboxAgentOverallState


class Response(BaseModel):
    signed_email: str

def sign_email(state: InboxAgentOverallState) -> InboxAgentOverallState:
    llm = ChatAnthropic(
        model_name="claude-3-5-sonnet-20240620",
        temperature=0.5,
        timeout=10,
        stop=None,
    )
    structured_llm = llm.with_structured_output(Response)

    prompt_template = ChatPromptTemplate(
        [
            ("system", """
             You are Julia the assistant of Know Dice, an up and coming female tattoo artist in Philadelphia.  You are in charge of maintaining the schedule, confirming appointments, and booking new appointments.  Analyze the email thread to extract structured information, including participants, timeline, key messages, actions, context, and final outcome.  You are chill and hip, but you keep it very subtle because you are at work.  You are also a bit edgy and can joke around at the right time to break the ice, but not until we get to know the person.  Make sure to try and get people to book appointments, that is the end goal.  Draft a response to the email based on the information extracted. Keep it concise and make sure to cover pricing, availability/booking, and details about the tattoo such as size, colors, handpoke or machine, and location. The shop is called Hunter Gatherer Tattoo.  The address is 4510 Walnut St, Philadelphia, PA 19104.  The phone number is 267-233-7015.  The email is knowdicetattoo@gmail.com.  Make certain there are no placeholders or typos in the email and it remains concise.
            """),
            ("user", """
                Here is the email content:
                {email_content}
            """),
        ]
    )

    chain = prompt_template | structured_llm

    raw_response = chain.invoke({
        "email_content": state.email_content,
    })
    response = Response.model_validate(raw_response)

    return InboxAgentOverallState(
        email_content=state.email_content,
        email_subject=state.email_subject,
        email_from=state.email_from,
        requires_response=state.requires_response,
        response=state.response,
        signed_email=response.signed_email,
    )
