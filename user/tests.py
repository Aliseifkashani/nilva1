import requests
from django.test import TestCase

from user.models import User


class TestJWTAuthentication(TestCase):

    def test_api_token(self):
        url = 'http://127.0.0.1:8000/api/token/'
        self.user = User.objects.create(username='a', password='a')
        self.user.save()
        result = requests.post(url, {'username': self.user.username, 'password': 'a'}).json()
        self.assertTrue('access' in result)