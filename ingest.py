from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime

from parser import parse_description

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)

creds = flow.run_local_server(port=0)
service = build('calendar', 'v3', credentials=creds)
now = datetime.datetime.utcnow().isoformat() + 'Z'

events_results = service.events().list(
    calendarId = '9ba2599fcbcf7a5c2f1c6a83ea7a94498d2f81d1185e44806a221c26e83e4db7@group.calendar.google.com',
    maxResults = 100,
    singleEvents = True,
    orderBy = 'startTime'
).execute()

events = events_results.get('items', [])

if not events:
    print('לא נמצאו פעילות')

for event in events:
    start = event['start'].get('dateTime', event['start'].get('date'))
    title = event.get('summary', '')
    description = event.get('description', '')

    parsed = parse_description(description)
    print("פעילות:", title)
    print(parsed)
    print('-'* 50)

def get_activities():
    activity_list = []
    for event in events:
        title = event.get('summary', '')
        description = event.get('description', '')

        parsed = parse_description(description)
        parsed["title"] = title
        activity_list.append(parsed)

    return activity_list
