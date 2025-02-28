from typing import Literal, Union, Any, Optional, List  
from enum import Enum

from pydantic import BaseModel, Field

class BookingIntent(str, Enum):
    BOOK_DATE = "book_date"
    FIND_DATE = "find_date"
    RESCHEDULE = "reschedule"
    CANCEL = "cancel"
    NONE = "none"

class ValidResponse(BaseModel):
    requires_response: Literal[True]
    reason: str

class InvalidResponse(BaseModel):
    requires_response: Literal[False]
    reason: str

class TattooBookingAgentOverallState(BaseModel):
    email: dict[str, Any] = Field(..., description="The email to be processed")
    requires_response: bool = Field(default=False, description="Whether the tattoo artist should respond to the email")

    extracted_dates: Optional[List[str]] = Field(default=None, description="The dates extracted from the email")
    extracted_notes: Optional[str] = Field(default=None, description="The notes extracted from the email")
    extracted_intent: Optional[BookingIntent] = Field(default=None, description="The intent extracted from the email")
    gcal_appointments: Optional[List[dict[str, Any]]] = Field(default=None, description="The appointments found in the user's Google Calendar for the dates extracted from the email")
    duration_hours: Optional[int] = Field(default=None, description="The duration of the tattoo session in hours")
    booking_date_start: Optional[str] = Field(default=None, description="The start date of the booking session in ISO format")
    booking_hours_start: Optional[str] = Field(default=None, description="The start time of the booking session in HH:MM format")
    response: Optional[str] = Field(default=None, description="The response to the email")