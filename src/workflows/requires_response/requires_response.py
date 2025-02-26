from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from agents.inbox_agent.types import InboxAgentOverallState


class Response(BaseModel):
    requires_response: bool = Field(description="Whether Cam should respond to the email")

def should_respond_to_email(state: InboxAgentOverallState) -> InboxAgentOverallState:
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
            ("system", "You are the assistant of Know Dice, an up and coming female tattoo artist in Philadelphia.  You are in charge of maintaining the schedule, confirming appointments, and booking new appointments.  Analyze the email thread to extract structured information, including participants, timeline, key messages, actions, context, and final outcome.  Determine if a response is required based on explicit requests or unresolved issues, and return the output in the structured format defined by the Response model."),
            ("human", "{email_content}"),
        ],
    )

    chain = prompt_template | structured_llm

    raw_response = chain.invoke({
        "email_content": state.email_content,
    })
    response = Response.model_validate(raw_response)

    if response.requires_response:
        return InboxAgentOverallState(
            email_content=state.email_content,
            email_subject=state.email_subject,
            email_from=state.email_from,
            requires_response=True,
        )
    else:
        return InboxAgentOverallState(
            email_content=state.email_content,
            email_subject=state.email_subject,
            email_from=state.email_from,
            requires_response=False,
        )
