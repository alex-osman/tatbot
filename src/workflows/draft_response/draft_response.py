from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from agents.inbox_agent.types import InboxAgentOverallState


class Response(BaseModel):
    response: str

def draft_response(state: InboxAgentOverallState) -> InboxAgentOverallState:
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
                You are an assistant that drafts a response to an email.
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
        requires_response=state.requires_response,
        response=response.response,
    )