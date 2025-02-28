import datetime
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

DEFAULT_TOKEN_FILE = "token.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]
GCAL_ID = os.getenv("GCAL_ID")  

class GCalSearch:
    def __init__(self, token_file: str = DEFAULT_TOKEN_FILE) -> None:
        self.credentials = Credentials.from_authorized_user_file(
            token_file, scopes=["https://mail.google.com/"]
        )
        self.api_resource = build(
            "calendar",
            "v3",
            credentials=self.credentials,
        )
        
        
        
    def get_appointments_for_date(self, date: str):
        """Fetch all scheduled events for a given date."""
        start_time = f"{date}T00:00:00Z"
        end_time = f"{date}T23:59:59Z"

        events_result = self.api_resource.events().list(
            calendarId=GCAL_ID,
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])
        return events  # List of booked appointments

    def find_available_slots(self, date: str, duration_hours: int):
        """Find open time slots of the requested duration on a given date."""
        events = self.get_appointments_for_date(date)

        work_start = datetime.strptime(date + " 10:00", "%Y-%m-%d %H:%M")  # Start workday at 10 AM
        work_end = datetime.strptime(date + " 20:00", "%Y-%m-%d %H:%M")  # End at 8 PM

        available_slots = []
        last_end = work_start

        for event in events:
            event_start = datetime.fromisoformat(event["start"]["dateTime"][:-1])
            event_end = datetime.fromisoformat(event["end"]["dateTime"][:-1])

            # Check if there's a gap long enough before this event
            gap_duration = (event_start - last_end).total_seconds() / 3600
            if gap_duration >= duration_hours:
                available_slots.append((last_end.strftime("%H:%M"), event_start.strftime("%H:%M")))

            last_end = event_end  # Move the pointer

        # Check for available time after the last event
        final_gap = (work_end - last_end).total_seconds() / 3600
        if final_gap >= duration_hours:
            available_slots.append((last_end.strftime("%H:%M"), work_end.strftime("%H:%M")))

        return available_slots  # List of (start, end) tuples

    def book_appointment(self, title, description, date, start_time, duration_hours):
        """Create a new appointment event in Google Calendar."""
        # Parse the datetime string using datetime.strptime instead of fromisoformat
        start_datetime = datetime.datetime.strptime(f"{date}T{start_time}:00", "%Y-%m-%dT%H:%M:%S")
        end_datetime = (start_datetime + datetime.timedelta(hours=duration_hours)).strftime("%Y-%m-%dT%H:%M:%S-05:00")
        start_datetime = start_datetime.strftime("%Y-%m-%dT%H:%M:%S-05:00")

        event = {
            "summary": f"{title}",
            "description": description,
            "start": {"dateTime": start_datetime, "timeZone": "America/New_York"},
            "end": {"dateTime": end_datetime, "timeZone": "America/New_York"},
        }
        print("using cal id", os.getenv("GCAL_ID"))

        event_result = self.api_resource.events().insert(calendarId=os.getenv("GCAL_ID"), body=event).execute()
        return event_result
