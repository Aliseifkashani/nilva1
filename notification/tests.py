import requests
from django.core import mail
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.test import TestCase
from kavenegar import KavenegarAPI, APIException, HTTPException
from datetime import datetime, timedelta

from .tasks import hello_test
from nilva1.celery_app import app
from user.models import User
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
        self.assertTrue('access' in response_dict)


class TestSendNotifications(TestCase):
    global user
    user = User.objects.get(username='mohammadali')

    # these 2 first tests need VPN for connecting
    def test_validate_email_correct_address(self):
        pass
        # email_address = "nilva.info@gmail.com"
        # response = requests.get(
        #     "https://isitarealemail.com/api/email/validate",
        #     params={'email': email_address})
        #
        # status = response.json()['status']
        # self.assertEqual(status, 'valid')

    def test_validate_email_incorrect_address(self):
        pass
        # email_address = "nilva1.info@gmail.com"
        # response = requests.get(
        #     "https://isitarealemail.com/api/email/validate",
        #     params={'email': email_address})
        #
        # status = response.json()['status']
        # self.assertEqual(status, 'invalid')

    # these 2 tests do nothing and just pass
    # we can't send email from tests
    def test_send_email_to_one_person(self):
        context = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'title': 'notif.title',
            'description': 'notif.description'
        }
        html_message = render_to_string('mail_template.html', context=context)
        try:
            mail.send_mail(
                'notif.title',
                'notif.content',
                'nilva.info@gmail.com',
                ['seifkashani14@gmail.com', user.email],  # just one email to one person
                html_message=html_message,
                fail_silently=False
            )
            self.assertTrue(True)
        except Exception:
            self.assertFalse(True)

    def test_send_email_to_multiple_people(self):
        context = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'title': 'notif.title',
            'description': 'notif.description'
        }
        html_message = render_to_string('mail_template.html', context=context)
        try:
            mail.send_mail(
                'notif.title',
                'notif.content',
                'nilva.info@gmail.com',
                [user.email, 'hasanzadeh@nilva.ir'],
                html_message=html_message,
                fail_silently=False
            )
            self.assertTrue(True)
        except Exception:
            self.assertFalse(True)

    def test_send_sms_to_one_person(self):
        pass
        try:
            api = KavenegarAPI(
                '51474735396C536947576930554D724332327075506E78667532482B58462B71672B5A7148554E753939733D',
            )
            params = {
                # 'sender': '1000596446',  # optional
                'receptor': '09019153618',  # multiple mobile number, split by comma
                'message': 'notif.title' + '\n\n' + 'notif.description' + '\n\n' + 'Nilva team',
            }
            response = api.sms_send(params)
            # print(response)
        except APIException as e:
            print(e)
        except HTTPException as e:
            print(e)

    def test_send_sms_to_multiple_people(self):
        pass


class TestSchedularNotification(TestCase):
    # in a terminal window run "celery -A nilva1 beat -l INFO"
    # in another terminal window run "celery -A nilva1 worker -l INFO"
    # then run tests
    def test_specific_time(self):
        task = hello_test.apply_async(
            args=('notif',),
            kwargs={'notif': 'notif'},
            eta=datetime.now() + timedelta(seconds=5)
        )

    def test_timedelta(self):
        task = hello_test.apply_async(
            args=('notif',),
            kwargs={'notif': 'notif'},
            countdown=10
        )
