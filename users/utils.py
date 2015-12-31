from datetime import date

from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import six
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.encoding import force_bytes
from django.utils.http import base36_to_int, int_to_base36

from .compat import urlsafe_base64_encode
from .conf import settings

try:
    from django.contrib.sites.shortcuts import get_current_site
except ImportError:  # pragma: no cover
    from django.contrib.sites.models import get_current_site

try:
    from django.db.models.signals import post_migrate
except ImportError:  # pragma: no cover
    from django.db.models.signals import post_syncdb as post_migrate


if settings.USERS_CREATE_SUPERUSER:
    try:
        # create_superuser is removed in django 1.7
        from django.contrib.auth.management import create_superuser
    except ImportError:  # pragma: no cover
        pass
    else:
        # Prevent interactive question about wanting a superuser created.
        from django.contrib.auth import models as auth_app
        post_migrate.disconnect(
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
        print('Creating superuser ({0}:{1})'.format(email, password))
        User.objects.create_superuser(email, password)

post_migrate.connect(auto_create_superuser, sender=None)


class EmailActivationTokenGenerator(object):

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
        login_timestamp = '' if user.last_login is None else \
            user.last_login.replace(microsecond=0, tzinfo=None)
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
