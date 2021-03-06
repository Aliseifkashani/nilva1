from datetime import timedelta
from django.core.mail import send_mail
from kavenegar import *
from django.template.loader import render_to_string

from notification_service.celery_app import app
from notification.serializers import NotificationSerializer
from user.models import User

SECONDS_OF_HOUR = 3600


@app.task
def add_notif_task(serializer):
    notif = serializer.instance
    notif_types = notif.notification_types.split(', ')

    # apply_async function needs json serializable data in kwargs. serializer itself isn't json serializable.
    global task
    for notif_type in notif_types:
        if notif_type.lower() == 'email':
            task = email_notif.apply_async(
                kwargs={'data': serializer.data},
                eta=notif.time_to_send
            )
        elif notif_type.lower() == 'sms':
            task = SMS_notif.apply_async(
                kwargs={'data': serializer.data},
                eta=notif.time_to_send
            )
        elif notif_type.lower() == 'telegram bot':
            task = telegram_notif.apply_async(
                kwargs={'data': serializer.data},
                eta=notif.time_to_send
            )
        elif notif_type.lower() == 'firebase':
            task = firebase_notif.apply_async(
                kwargs={'data': serializer.data},
                eta=notif.time_to_send
            )
        elif notif_type.lower() == 'google calendar':
            task = google_calendar_notif.apply_async(
                kwargs={'data': notif},
                eta=notif.time_to_send
            )

    notif.task_id = task.id
    if notif.repeat > 0:
        notif.repeat -= 1
    notif.save()
    serializer = NotificationSerializer(notif)  # we need it for resume_task.apply_async

    if notif.repeat > 0 or notif.repeat == -1:
        task = resume_task.apply_async(
            kwargs={'data': serializer.data},
            eta=notif.time_to_send + timedelta(hours=notif.interval)
        )
        notif.task_id += ', ' + task.id
        notif.save()


# We needed another function for implementing resuming tasks because we couldn't call add_notif_task.apply_async in
# itself. Also we couldn't have add_notif_task with specific repetition with custom interval.
@app.task
def resume_task(data):
    serializer = NotificationSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
    notif = serializer.instance

    # notif.notification_types is a string like 'email, sms, telegram bot'
    notif_types = notif.notification_types.split(', ')

    for notif_type in notif_types:
        if notif_type.lower() == 'email':
            email_notif(serializer.data)
        elif notif_type.lower() == 'sms':
            SMS_notif(serializer.data)
        elif notif_type.lower() == 'telegram bot':
            telegram_notif(serializer.data)
        elif notif_type.lower() == 'firebase':
            firebase_notif(serializer.data)
        elif notif_type.lower() == 'google calendar':
            google_calendar_notif(serializer.data)

    if notif.repeat > 0:
        notif.repeat -= 1
    notif.save()
    serializer = NotificationSerializer(notif)  # we need it for resume_task.apply_async

    if notif.repeat > 0 or notif.repeat == -1:
        task = resume_task.apply_async(
            kwargs={'data': serializer.data},
            countdown=notif.interval * SECONDS_OF_HOUR
        )
        notif.task_id = task.id
        notif.save()


@app.task
def edit_notif_task(serializer):
    # straight task update isn't implemented in celery
    notif = serializer.instance
    task_ids = notif.task_id.split(', ')
    for task_id in task_ids:
        app.control.revoke(task_id=task_id, terminate=True)

    add_notif_task(serializer)


@app.task
def delete_notif_task(serializer):
    notif = serializer.instance
    task_ids = notif.task_id.split(', ')
    for task_id in task_ids:
        app.control.revoke(task_id=task_id, terminate=True)


@app.task
def email_notif(data):
    serializer = NotificationSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
    notif = serializer.instance

    relevant_staff = notif.relevant_staff.split(', ')
    for staff in relevant_staff:
        user = User.objects.get(username=staff)
        context = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'title': notif.title,
            'description': notif.description,
        }
        html_message = render_to_string('mail_template.html', context=context)
        send_mail(
            notif.title,
            notif.description,
            'nilva.info@gmail.com',
            [user.email],
            html_message=html_message,
            fail_silently=False
        )


@app.task
def SMS_notif(data):
    serializer = NotificationSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
    notif = serializer.instance
    relevant_staff = notif.relevant_staff.split(', ')

    try:
        api = KavenegarAPI(
            '51474735396C536947576930554D724332327075506E78667532482B58462B71672B5A7148554E753939733D',
        )
        for staff_username in relevant_staff:
            params = {
                # 'sender': '1000596446',  # optional
                'receptor': User.objects.get(username=staff_username).phone,  # multiple mobile number, split by comma
                'message': notif.title + '\n\n' + notif.description + '\n\n' + 'Nilva team',
            }
            response = api.sms_send(params)
            print(response)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)


@app.task
def telegram_notif(data):
    pass
    # need for requesting to telegram bot service for send_notif


@app.task
def firebase_notif(data):
    pass
    # should be implemented in another process


@app.task
def google_calendar_notif(data):
    pass
    # should be implemented in another process


# testing:
@app.task
def hello_test(data):
    print(data)

# task = hello_test.apply_async(
#     kwargs={'data': 'notif'},
#     countdown=2,
#     expires=10
# )
