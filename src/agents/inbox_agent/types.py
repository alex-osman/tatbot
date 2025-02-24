from typing import Literal, Union

from pydantic import BaseModel, Field


class ValidResponse(BaseModel):
    requires_response: Literal[True]
    reason: str

class InvalidResponse(BaseModel):
    requires_response: Literal[False]
    reason: str

class InboxAgentOverallState(BaseModel):
    email_content: str
    requires_response: bool = Field(default=False, description="Whether the email requires a response")
    response: Union[str, None] = Field(default=None, description="The response to the email")
    valid_response: Union[ValidResponse, InvalidResponse, None] = Field(default=None, description="Whether the response is valid")
