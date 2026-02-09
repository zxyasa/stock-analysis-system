import json
from pathlib import Path
from datetime import datetime, date, time, timedelta

import pytz
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = Path('secrets/google-calendar/token.json')
SCOPES = ['https://www.googleapis.com/auth/calendar']
USER_TZ = pytz.timezone('Australia/Sydney')


def iso(dt):
    if isinstance(dt, datetime):
        return dt.isoformat()
    return dt


def main():
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    service = build('calendar', 'v3', credentials=creds)

    now = datetime.now(USER_TZ)
    tomorrow = now.date() + timedelta(days=1)
    start_dt = USER_TZ.localize(datetime.combine(tomorrow, time(0, 0)))
    end_dt = start_dt + timedelta(days=1)

    time_min = start_dt.isoformat()
    time_max = end_dt.isoformat()

    calendars_resp = service.calendarList().list().execute()
    events_out = []
    for cal in calendars_resp.get('items', []):
        cal_id = cal['id']
        cal_summary = cal.get('summaryOverride') or cal.get('summary')
        events_resp = service.events().list(
            calendarId=cal_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        for event in events_resp.get('items', []):
            start = event.get('start', {})
            end = event.get('end', {})
            start_time = start.get('dateTime') or start.get('date')
            end_time = end.get('dateTime') or end.get('date')
            events_out.append({
                'calendar': cal_summary,
                'summary': event.get('summary', '(无标题)'),
                'start': start_time,
                'end': end_time,
                'htmlLink': event.get('htmlLink')
            })

    events_out.sort(key=lambda e: e['start'])

    print(json.dumps({
        'timezone': USER_TZ.zone,
        'date': tomorrow.isoformat(),
        'events': events_out
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
