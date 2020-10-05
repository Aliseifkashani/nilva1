import requests
from django.test import TestCase
import unittest
from unittest.mock import patch

from . import views


class TestJWTAuthentication(unittest.TestCase):

    def test_api_token(self):
        pass


class TestNotifications(unittest.TestCase):

    def test_get(self):
        url = 'http://127.0.0.1:8000/get/'
        result = requests.get(url)


# Create your tests here.

if __name__ == '__main__':
    unittest.main()
