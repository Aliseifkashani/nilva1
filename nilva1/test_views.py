from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import render_to_string


def educational(request):
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
        ['seifkashani14@gmail.com', ],  # just one email to one person
        html_message=html_message,
        fail_silently=False
    )
    return HttpResponse('Successful operation')