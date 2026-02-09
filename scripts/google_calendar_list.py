import json
from pathlib import Path

import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = Path('secrets/google-calendar/token.json')
SCOPES = ['https://www.googleapis.com/auth/calendar']


def main():
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    service = build('calendar', 'v3', credentials=creds)
    calendars = service.calendarList().list().execute()
    for item in calendars.get('items', []):
        print(f"- {item.get('summary')} ({item.get('id')})")


if __name__ == '__main__':
    main()
