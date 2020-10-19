import ast , subprocess
import os

import requests
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import reverse
from kavenegar import KavenegarAPI, APIException, HTTPException
from datetime import datetime, timedelta
from rest_framework.test import APIClient
from celery.worker.control import revoke

from .serializers import NotificationSerializer
from .tasks import hello_test
from user.models import User
from .tasks import add_notif_task


class TestJWTAuthentication(TestCase):

    def test_api_token(self):
        url = 'http://127.0.0.1:8000/api/token/'
        user = User.objects.get(username='mohammadali')
        data = {
            'username': user.username,
            'password': user.password
        }
        result = requests.post(url, data)
        response_dict = eval(result.text)
        self.assertTrue('access' in response_dict)


class TestSendNotifications(TestCase):
    # global user
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
            send_mail(
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
            send_mail(
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

    # for now you need to check visually

    def test_specific_time(self):
        hello_test.apply_async(
            kwargs={'data': 'task with specific time'},
            eta=datetime.now()-timedelta(minutes=210)+timedelta(seconds=5)  # timezone of celery is utc for now
        )

    def test_countdown(self):
        hello_test.apply_async(
            kwargs={'data': 'task with countdown'},
            countdown=10
        )

    def test_repeat_interval(self):
        context = {
            "title": "test_add1",
            "description": "salevat befreis",
            "creator": "mohammadali",
            "relevant_staff": "mohammadali",
            "time_created": datetime.now(),
            "buffer_time": "2020-10-04 12:30",
            "time_to_send": datetime.now()-timedelta(minutes=210)+timedelta(seconds=1),  # timezone of celery is utc
            # for now
            "notification_types": "sms",
            "repeat": 2,
            "interval": 1,
            "task_id": ""
        }
        serializer = NotificationSerializer(data=context)
        if serializer.is_valid():
            serializer.save()
        add_notif_task(serializer)
        # os.system('celery -A nilva1 worker -l INFO')
        # subprocess.call('python manage.py test notification.tests.TestSchedularNotification.test_repeat_interval')
        serializer.instance.delete()

    def test_edit_task(self):
        task = hello_test.apply_async(
            kwargs={'data': 'editing task'},
            countdown=10
        )
        revoke(task_id=task.id, terminate=True, state=200)
        hello_test.apply_async(
            kwargs={'data': 'edited task'},
            countdown=3
        )

    def test_delete_task(self):
        task = hello_test.apply_async(
            kwargs={'data': 'deleting task'},
            countdown=3
        )
        revoke(task_id=task.id, terminate=True, state=200)


class TestNotificationOperationsViews(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='a', password='a')
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {'username': 'a', 'password': 'a'})
        self.token = response.data['access']
        self.header = {'Authorization': f'Bearer {self.token}'}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_add_notification(self):
        context = {
            "title": "test_add",
            "description": "salevat befreis",
            "creator": "mohammadali",
            "relevant_staff": "mohammadali",
            "time_created": "2020-10-04 12:30",
            "buffer_time": "2020-10-04 12:30",
            "time_to_send": "2020-10-04 12:30",
            "notification_types": "email, sms, telegram bot, firebase, google calendar",
            "repeat": 1,
            "interval": 24,
            "task_id": ""
        }
        response = self.client.post(reverse('add_notification'), data=context)
        dict_str = response.content.decode("UTF-8")
        mydata = ast.literal_eval(dict_str)
        self.assertTrue('id' in mydata)

    def test_get_notifications(self):
        context = {
            "title": "test_add1",
            "description": "salevat befreis",
            "creator": "mohammadali",
            "relevant_staff": "mohammadali",
            "time_created": "2020-10-04 12:30",
            "buffer_time": "2020-10-04 12:30",
            "time_to_send": "2020-10-04 12:30",
            "notification_types": "email, sms, telegram bot, firebase, google calendar",
            "repeat": 1,
            "interval": 24,
            "task_id": ""
        }
        self.client.post(reverse('add_notification'), data=context)
        context = {
            "title": "test_add2",
            "description": "salevat befreis",
            "creator": "mohammadali",
            "relevant_staff": "mohammadali",
            "time_created": "2020-10-04 12:30",
            "buffer_time": "2020-10-04 12:30",
            "time_to_send": "2020-10-04 12:30",
            "notification_types": "email, sms, telegram bot, firebase, google calendar",
            "repeat": 1,
            "interval": 24,
            "task_id": ""
        }
        self.client.post(reverse('add_notification'), data=context)
        response = self.client.get(reverse('get_notification'))
        # print(response.content)
        self.assertTrue('id' in list(response.data[0].items())[0])
        self.assertTrue('id' in list(response.data[1].items())[0])

    def test_edit_notification(self):
        context = {
            "title": "test_edit_before",
            "description": "salevat befreis",
            "creator": "mohammadali",
            "relevant_staff": "mohammadali",
            "time_created": "2020-10-04 12:30",
            "buffer_time": "2020-10-04 12:30",
            "time_to_send": "2020-10-04 12:30",
            "notification_types": "email, sms, telegram bot, firebase, google calendar",
            "repeat": 1,
            "interval": 24,
            "task_id": ""
        }
        response = self.client.post(reverse('add_notification'), data=context)
        print(response.content)
        dict_str = response.content.decode("UTF-8")
        mydata = ast.literal_eval(dict_str)
        context = {
            "id": mydata['id'],
            "title": "test_edit_after",
            "description": "salevat befreis",
            "creator": "mohammadali",
            "relevant_staff": "mohammadali",
            "time_created": "2020-10-04 12:30",
            "buffer_time": "2020-10-04 12:30",
            "time_to_send": "2020-10-04 12:30",
            "notification_types": "email, sms, telegram bot, firebase, google calendar",
            "repeat": 1,
            "interval": 24,
            "task_id": ""
        }
        response = self.client.patch(reverse('edit_notification'), data=context)
        dict_str = response.content.decode("UTF-8")
        mydata = ast.literal_eval(dict_str)
        self.assertEqual(mydata['title'], 'test_edit_after')

    def test_delete_notification(self):
        context = {
            "title": "test_add",
            "description": "salevat befreis",
            "creator": "mohammadali",
            "relevant_staff": "mohammadali",
            "time_created": "2020-10-04 12:30",
            "buffer_time": "2020-10-04 12:30",
            "time_to_send": "2020-10-04 12:30",
            "notification_types": "email, sms, telegram bot, firebase, google calendar",
            "repeat": 1,
            "interval": 24,
            "task_id": ""
        }
        response = self.client.post(reverse('add_notification'), data=context)
        dict_str = response.content.decode("UTF-8")
        mydata = ast.literal_eval(dict_str)
        response = self.client.delete(reverse('delete_notification'), data={'id': mydata['id']})
        dict_str = response.content.decode("UTF-8")
        self.assertTrue('null' in dict_str)


class TestCalendarScheduling(TestCase):
    pass
