from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string

from .serializers import User


def email_generator(username):
    user = get_object_or_404(User, username=username)
    user.confirmation_code = get_random_string(15)
    user.save()
    send_mail(
        'Ваш код подтверждения',
        f'Ваш код подтверждения: {user.confirmation_code}',
        'from@example.com',
        [user.email],
        fail_silently=False,
    )
