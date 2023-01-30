from __future__ import print_function

import datetime
import os.path


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def main():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        ms = input("podaj numer miesiaca: ")
        days = input("podaj dni dziennej zmiany odzielone '+': ")
        ndays = input("podaj dni nocnej zmiany odzielone '+': ")
        dayshift = days.split('+')
        nightshift = ndays.split('+')
        for d in dayshift:
            event = {
                'summary': 'Dniowka',
                'colorId': 10,
                'start': {'dateTime': f'2023-{ms}-{d}T07:00:00',
                'timeZone': 'Europe/Warsaw'},
                'end': {'dateTime': f'2023-{ms}-{d}T07:00:00',
                'timeZone': 'Europe/Warsaw'},
                'reminders': {'useDefault': False,
                              'overrides': [{'method': 'popup', 'minutes': 120}]}
            }
            event = service.events().insert(calendarId='primary', body=event).execute()
            print('Event created: %s' % (event.get('htmlLink')))

        for d in nightshift:
            event = {
                'summary': 'Nocka',
                'colorId': 11,
                'start': {'dateTime': f'2023-{ms}-{d}T19:00:00',
                'timeZone': 'Europe/Warsaw'},
                'end': {'dateTime': f'2023-{ms}-{d}T19:00:00',
                'timeZone': 'Europe/Warsaw'},
                'reminders': {'useDefault': False,
                              'overrides': [{'method': 'popup', 'minutes': 120}]}
            }
            event = service.events().insert(calendarId='primary', body=event).execute()
            print('Event created: %s' % (event.get('htmlLink')))

        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=20, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()
