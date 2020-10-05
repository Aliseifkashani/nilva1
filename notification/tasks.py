from datetime import timedelta
from celery.worker.control import revoke
from django.core.mail import send_mail
from kavenegar import *
from django.template.loader import render_to_string

from nilva1.celery import app
from user.models import User


@app.task
def add_notif_task(serializer):
    notif = serializer.instance
    global task
    for notif_type in notif.notification_types:
        if notif_type.lower() == 'email':
            task = email_notif.apply_async(
                args=('notif',),
                kwargs={'notif': notif},
                eta=notif.time_to_send
            )
        elif notif_type.lower() == 'sms':
            task = SMS_notif.apply_async(
                args=('notif',),
                kwargs={'notif': notif},
                eta=notif.time_to_send
            )
        elif notif_type.lower() == 'telegram_message':
            task = telegram_notif.apply_async(
                args=('notif',),
                kwargs={'notif': notif},
                eta=notif.time_to_send
            )
        elif notif_type.lower() == 'firebase_message':
            task = firebase_notif.apply_async(
                args=('notif',),
                kwargs={'notif': notif},
                eta=notif.time_to_send
            )
        # elif notif_type.lower() == 'google_calendar':
        #     task = firebase_notif.apply_async(
        #         args=('notif',),
        #         kwargs={'notif': notif},
        #         eta=notif.time_to_send
        #     )

    notif.task_id = task.id

    if notif.repeat > 0:
        notif.repeat -= 1

    notif.save()
    serializer.save()
    resume_task.apply_async(
        args=('notif',),
        kwargs={'notif': notif},
        countdown=timedelta(notif.interval)
    )


@app.task
def resume_task(serializer):
    notif = serializer.instance
    global task
    if notif.repeat > 0 or notif.repeat == -1:
        for notif_type in notif.notification_types:
            if notif_type.lower() == 'email':
                task = email_notif.apply_async(
                    args=('notif',),
                    kwargs={'notif': notif},
                    countdown=timedelta(notif.interval)
                )
            elif notif_type.lower() == 'sms':
                task = SMS_notif.apply_async(
                    args=('notif',),
                    kwargs={'notif': notif},
                    countdown=timedelta(notif.interval)
                )
            elif notif_type.lower() == 'telegram_message':
                task = telegram_notif.apply_async(
                    args=('notif',),
                    kwargs={'notif': notif},
                    countdown=timedelta(notif.interval)
                )
            elif notif_type.lower() == 'firebase_message':
                task = firebase_notif.apply_async(
                    args=('notif',),
                    kwargs={'notif': notif},
                    countdown=timedelta(notif.interval)
                )
        notif.task_id = task.id
    else:
        return

    if notif.repeat > 0:
        notif.repeat -= 1

    notif.save()
    serializer.save()
    resume_task.apply_async(
        args=('notif',),
        kwargs={'notif': notif},
        countdown=timedelta(notif.interval)
    )


@app.task
def edit_notif_task(serializer):
    notif = serializer.instance
    revoke(task_id=notif.task_id, terminate=True)
    add_notif_task(notif)


@app.task
def delete_notif(serializer):
    notif = serializer.instance
    notif.repeat = -2
    revoke(task_id=notif.task_id, terminate=True)


@app.task
def email_notif(notif):
    for staff in notif.relevant_staff:
        user = User.objects.get(username=staff)
        context = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'title': notif.title,
            'description': notif.description
        }
        html_message = render_to_string('mail_template.html', context=context)
        send_mail(
            notif.title,
            notif.content,
            'nilva.info@gmail.com',
            [user.email],
            html_message=html_message,
            fail_silently=False
        )


@app.task
def SMS_notif(notif):
    try:
        api = KavenegarAPI(
            '51474735396C536947576930554D724332327075506E78667532482B58462B71672B5A7148554E753939733D',
        )
        params = {
            # 'sender': '1000596446',# optional
            'receptor': notif.relevant_staff,  # multiple mobile number, split by comma
            'message': notif.title + '\n\n' + notif.description + '\n\n' + 'Nilva team',
        }
        response = api.sms_send(params)
        print(response)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)


@app.task
def telegram_notif(notif):
    pass
    # TOKEN = '1254140072:AAEpWrOpCmQM4DZ-RIO00i1tcK5QslbKU6Q'
    # bot = TeleBot(TOKEN)
    #
    # for user in notif.relevant_staff:
    #     bot.send_message(user.chat_id, notif.title + '\n\n' + notif.description)


@app.task
def firebase_notif(notif):
    pass


@app.task
def google_calendar_notif(notif):
    pass
