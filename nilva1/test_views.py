from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import render_to_string

from user.models import User


def test_send_email_to_multiple_people(request):
    context = {
        'first_name': 'user.first_name',
        'last_name': 'user.last_name',
        'title': 'notif.title',
        'description': 'notif.description'
    }
    html_message = render_to_string('mail_template.html', context=context)
    send_mail(
        'notif.title',
        'notif.content',
        'nilva.info@gmail.com',
        ['seifkashani14@gmail.com', ''],
        html_message=html_message,
        fail_silently=False
    )
    return HttpResponse('Successful operation')


def educational(request):
    return HttpResponse(User.objects.get(username='a').password)