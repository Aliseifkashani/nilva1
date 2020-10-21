import webbrowser
import requests


def test_send_email():
    url = 'http://127.0.0.1:8000/educational/'
    requests.get(url)
    # webbrowser.open(url)


test_send_email()
