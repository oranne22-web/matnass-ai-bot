from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime
from parser import parse_description

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_service():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    return build('calendar', 'v3', credentials=creds)

def fetch_events():
    service = get_calendar_service()

    events_results = service.events().list(
        calendarId = '9ba2599fcbcf7a5c2f1c6a83ea7a94498d2f81d1185e44806a221c26e83e4db7@group.calendar.google.com',
        maxResults = 100,
        singleEvents = True,
        orderBy = 'startTime'
    ).execute()

    return events_results.get('items', [])


def get_activities():
    events = fetch_events()
    activity_list = []
    for event in events:
        title = event.get('summary', '')
        description = event.get('description', '')

        parsed = parse_description(description)
        parsed["title"] = title
        activity_list.append(parsed)

    return activity_list
