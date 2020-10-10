import requests
from django.test import TestCase

from . import views


class TestJWTAuthentication(TestCase):

    def test_api_token(self):
        url = 'http://127.0.0.1:8000/api/token/'
        data = {
            'username': 'mohammadali',
            'password': 'ali25202520'
        }
        result = requests.post(url, data)
        response_dict = eval(result.text)
        self.assertContains(response_dict, 'token')


class TestNotifications(TestCase):
    pass
