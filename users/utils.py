from datetime import date
from django.utils import six

from django.db.models import signals
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import get_user_model
from django.contrib.auth.management import create_superuser
from django.contrib.auth import models as auth_app

from django.utils.http import int_to_base36, base36_to_int
from django.utils.crypto import constant_time_compare, salted_hmac

from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


try:
    from django.contrib.sites.shortcuts import get_current_site
except ImportError:
    from django.contrib.sites.models import get_current_site

from .conf import settings
from .exceptions import InvalidCode, CodeExpired


if settings.USERS_CREATE_SUPERUSER:
    # Prevent interactive question about wanting a superuser created.
    signals.post_syncdb.disconnect(
        create_superuser,
        sender=auth_app,
        dispatch_uid='django.contrib.auth.management.create_superuser')


def auto_create_superuser(sender, **kwargs):
    if not settings.USERS_CREATE_SUPERUSER:
        return

    email = settings.USERS_SUPERUSER_EMAIL
    password = settings.USERS_SUPERUSER_PASSWORD

    User = get_user_model()
    try:
        User.base_objects.get(email=email)
    except User.DoesNotExist:
        print('Creating superuser ({1}:{0})'.format(email, password))
        User.objects.create_superuser(email, password, is_active=True)

signals.post_syncdb.connect(auto_create_superuser, sender=None)


class EmailActivationTokenGenerator(object):

    @staticmethod
    def get_last_login_timestamp(user):
        if user.last_login is not None:
            return int(user.last_login.strftime('%s'))
        return 0

    def make_token(self, user):
        return self._make_token_with_timestamp(user, self._num_days(self._today()))

    def check_token(self, user, token):
        """
        Check that a activation token is correct for a given user.
        """
        # Parse the token
        try:
            ts_b36, hash = token.split('-')
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/uid has not been tampered with
        if not constant_time_compare(self._make_token_with_timestamp(user, ts), token):
            return False

        # Check the timestamp is within limit
        if (self._num_days(self._today()) - ts) > settings.USERS_EMAIL_CONFIRMATION_TIMEOUT_DAYS:
            return False

        return True

    def _make_token_with_timestamp(self, user, timestamp):

        ts_b36 = int_to_base36(timestamp)
        key_salt = 'users.utils.EmailActivationTokenGenerator'
        login_timestamp = self.get_last_login_timestamp(user)

        value = (six.text_type(user.pk) + six.text_type(user.email) +
                 six.text_type(login_timestamp) + six.text_type(timestamp))
        hash = salted_hmac(key_salt, value).hexdigest()[::2]
        return '%s-%s' % (ts_b36, hash)

    @staticmethod
    def _num_days(dt):
        return (dt - date(2001, 1, 1)).days

    @staticmethod
    def _today():
        # Used for mocking in tests
        return date.today()


def send_activation_email(
        user=None, request=None, from_email=None,
        subject_template='users/activation_email_subject.html',
        email_template='users/activation_email.html', html_email_template=None):

    if not user.is_active and settings.USERS_VERIFY_EMAIL:
        token_generator = EmailActivationTokenGenerator()

        current_site = get_current_site(request)

        context = {
            'email': user.email,
            'site': current_site,
            'expiration_days': settings.USERS_EMAIL_CONFIRMATION_TIMEOUT_DAYS,
            'user': user,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': token_generator.make_token(user=user),
            'protocol': 'https' if request.is_secure() else 'http',
        }

        subject = render_to_string(subject_template, context)
        # email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = render_to_string(email_template, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [user.email])
        if html_email_template is not None:
            html_email = render_to_string(html_email_template, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()
