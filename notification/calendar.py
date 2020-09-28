from datetime import timedelta
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
from googleapiclient.discovery import build

from .models import User, Notification


def add():
    notif = Notification.objects.latest('id')

    scopes = ['https://www.googleapis.com/auth/calendar']
    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', scopes=scopes)
    credentials = flow.run_console()
    pickle.dump(credentials, open('token.pkl', 'wb'))
    credentials = pickle.load(open('token.pkl', 'rb'))
    service = build('calendar', 'v3', credentials=credentials)
    result = service.calendarList().list().execute()
    calendar_id = result['items'][0]['id']

    relevant_staff = []
    for staff in notif.relevant_staff:
        relevant_staff.append({'email': User.objects.get(username=staff).email})

    event = {
        'summary': notif.title,
        # 'location': '800 Howard St., San Francisco, CA 94103',
        'description': notif.description,
        'start': {
            'dateTime': notif.time_to_send.strftime('%Y-%m-%dT%H:%M:%S'),
            'timeZone': 'Asia/Tehran',
        },
        'end': {
            'dateTime': (notif.time_to_send + timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%S'),
            'timeZone': 'Asia/Tehran',
        },
        'recurrence': [
            'RRULE:FREQ=DAILY;COUNT=3'
        ],
        'attendees': relevant_staff,
        'reminders': {
            'useDefault': False,
            'overrides': [
                # {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    event = service.events().insert(calendarId=calendar_id, body=event).execute()


def edit():
    pass


def delete():
    pass