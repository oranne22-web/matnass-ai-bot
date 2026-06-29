import os
import pickle
import datetime
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from parser import parse_description

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CALENDAR_ID = '9ba2599fcbcf7a5c2f1c6a83ea7a94498d2f81d1185e44806a221c26e83e4db7@group.calendar.google.com'
ISRAEL_TZ = ZoneInfo("Asia/Jerusalem")

def get_calendar_service():
    creds = None

    # אם יש טוקן שמור, טוענים אותו
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as f:
            creds = pickle.load(f)

    # אם אין טוקן או שפג תוקפו, מתחברים מחדש
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # שומרים את הטוקן לפעמים הבאות
        with open('token.pickle', 'wb') as f:
            pickle.dump(creds, f)
    return build('calendar', 'v3', credentials=creds)

def fetch_events() -> list:
    service = get_calendar_service()

    # קח אירועים לשלושה חודשים קדימה (כולל recurring)
    now = datetime.datetime.utcnow()
    time_min = now.isoformat() + 'Z'
    time_max = (now + datetime.timedelta(days=14)).isoformat() + 'Z'

    events_results = service.events().list(
        calendarId = CALENDAR_ID,
        maxResults=500,  # יותר תוצאות כדי לכסות recurring
        singleEvents=True,  # פורס recurring לאירועים בודדים
        orderBy='startTime',
        timeMin=time_min,
        timeMax=time_max,
    ).execute()

    return events_results.get('items', [])


def get_activities() -> list:
    events = fetch_events()
    activity_list = []
    seen_recurring = set()  # למנוע כפילויות של recurring

    for event in events:
        is_recurring = 'recurringEventId' in event  # גוגל מוסיף את זה לכל occurrence
        # אם recurring - רק פעם אחת לפי recurringEventId
        if is_recurring:
            recurring_id = event['recurringEventId']
            if recurring_id in seen_recurring:
                continue
            seen_recurring.add(recurring_id)

        title = event.get('summary', '')
        description = event.get('description', '')
        location = event.get('location', '')

        parsed = parse_description(description)
        parsed["title"] = title
        parsed['location'] = location
        parsed['is_recurring'] = is_recurring

        start_info = event.get('start', {})
        start_time = start_info.get('dateTime') or start_info.get('date', '')
        parsed['start_time'] = start_time

        activity_list.append(parsed)

    return activity_list
