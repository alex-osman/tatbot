from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from agents.inbox_agent.types import InboxAgentOverallState


class Response(BaseModel):
    signed_email: str

def sign_email(state: InboxAgentOverallState) -> InboxAgentOverallState:
    llm = ChatAnthropic(
        model_name="claude-3-5-sonnet-20240620",
        temperature=0,
        timeout=10,
        stop=None,
    )
    structured_llm = llm.with_structured_output(Response)

    prompt_template = ChatPromptTemplate(
        [
            ("system", """
                You are an assistant that signs an email as Know Dice's assistant Jennifer.  The shop is called Lombardo and Sons Tattoo Parlor.  The address is 130 N 12th St, Philadelphia, PA 19107.  The phone number is 215-922-8888.  The email is knowdicetattoo@gmail.com.  Make certain there are no placeholders or typos in the email.
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
