import re

from django.db.models import signals
from django.utils.translation import ugettext as _
from django.contrib.auth import get_user_model
from django.contrib.auth.management import create_superuser
from django.contrib.auth import models as auth_app

from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.core import signing
from django.utils.http import int_to_base36


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
        print 'Creating superuser (%s:%s)' % (email, password)
        User.objects.create_superuser(email, password, is_active=True)

signals.post_syncdb.connect(auto_create_superuser, sender=None)


class EmailActivationTokenGenerator(object):

    def __init__(self):
        self.salt = 'XREFOJ^O1Mx_RGalPt_o3fQCZ7Uw=*vHGTb=_YVp2bK4m16Zw^Du9gz1uyVs'
        self.signer = signing.TimestampSigner(salt=self.salt, sep='_')

    def get_last_login_timestamp(self, user):
        if user.last_login is not None:
            return int(user.last_login.strftime('%s'))
        return 0

    def make_token(self, user):
        if not user:
            raise NameError('A user instance is required to generate an activation token')
        code = [re.sub('[^A-Za-z0-9]+', '', user.email),
                str(user.id),
                int_to_base36(self.get_last_login_timestamp(user))]
        return self.signer.sign(u'-'.join(code))

    def validate_token(self, code):
        max_age = settings.USERS_EMAIL_CONFIRMATION_TIMEOUT_DAYS * 86400

        try:
            data = self.signer.unsign(code, max_age=max_age)
        except signing.SignatureExpired:
            raise CodeExpired(_('Activation key has expired'))
        except signing.BadSignature:
            raise InvalidCode(_('Unable to verify the activation key.'))

        parts = data.rsplit('-', 2)
        if len(parts) != 3:
            raise InvalidCode(_('Something went wrong while decoding the activation token.'))

        email, uid, timestamp = parts
        if uid and timestamp:
            User = get_user_model()
            try:
                user = User.objects.get(pk=uid)
            except (User.DoesNotExist, TypeError, ValueError):
                raise InvalidCode(_('Something went wrong while decoding the activation token.'))

            if timestamp != int_to_base36(self.get_last_login_timestamp(user)):
                raise InvalidCode(_('The link has already been used.'))

        else:
            user = None

        return user


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
