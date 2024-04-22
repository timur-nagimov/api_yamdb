from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string

from .serializers import User


def email_generator(username):
    user = get_object_or_404(User, username=username)
    user.confirmation_code = get_random_string(15)
    user.save()

    email_subject = 'Ваш код подтверждения'
    email_body = f'Ваш код подтверждения: {user.confirmation_code}'
    from_email = f"noreply@{settings.DOMAIN_NAME}"

    send_mail(
        email_subject,
        email_body,
        from_email,
        (user.email,),
    )
