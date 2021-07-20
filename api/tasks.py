from celery import shared_task
from django.core.mail import send_mail
from django.utils.timezone import now

from api.models import Tasks


@shared_task
def notifications():
    task = Tasks.objects.filter(date_to_check=now())
    for notif in task:
        subject = f"Повторение темы {notif.title} у {notif.user}"
        message = f"Сегодня {notif.date_to_check}, {notif.user} должен показать знания темы {notif.title}"
        from_email = 'gleb.lobinsky@mbicycle.com'
        user_email = notif.user.email
        manager_email = notif.manager.email
        send_mail(subject, message, from_email, [user_email, manager_email], fail_silently=False)
