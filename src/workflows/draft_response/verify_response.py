from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from agents.inbox_agent.types import (
    InboxAgentOverallState,
    InvalidResponse,
    ValidResponse,
)


class Response(BaseModel):
    is_valid_response: bool = Field(description="Whether the response is valid")
    reason: str = Field(description="The reason for the response")

def verify_response(state: InboxAgentOverallState) -> InboxAgentOverallState:
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
                You are an assistant that verifies if a response is valid and returns structured output.
            """),
            ("user", """
                Here is the email content:
                {email_content}

                Here is the response:
                {response}

                Please provide the structured output indicating whether the response is valid and the reason.
            """),
        ]
    )

    chain = prompt_template | structured_llm

    if state.response:
        raw_response = chain.invoke({
            "email_content": state.email_content,
            "response": state.response,
        })
        response = Response.model_validate(raw_response)

        return InboxAgentOverallState(
            email_content=state.email_content,
            email_subject=state.email_subject,
            email_from=state.email_from,
            response=state.response,
            valid_response=ValidResponse(
                requires_response=True,
                reason=response.reason,
            ),
        )
    else:
        return InboxAgentOverallState(
            email_content=state.email_content,
            email_subject=state.email_subject,
            email_from=state.email_from,
            response=state.response,
            valid_response=InvalidResponse(
                requires_response=False,
                reason="No response provided",
            ),
        )
