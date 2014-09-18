#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings

from users.conf import settings
from users.utils import (auto_create_superuser, EmailActivationTokenGenerator,
                         send_activation_email)


class CreateSuperuserTest(TestCase):

    user_email = 'user@example.com'
    user_password = 'pa$sw0Rd'

    @override_settings(USERS_CREATE_SUPERUSER=True,
                       USERS_SUPERUSER_EMAIL=user_email,
                       USERS_SUPERUSER_PASSWORD=user_password)
    def test_auto_create_superuser(self):
        auto_create_superuser(sender=None)

        user = get_user_model().objects.get(email=self.user_email)

        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


class SendActivationEmailTest(TestCase):

    user_email = 'user@example.com'
    user_password = 'pa$sw0Rd'

    @override_settings(USERS_VERIFY_EMAIL=True)
    def test_send_activation_email(self):
        factory = RequestFactory()
        request = factory.get(reverse('users_register'))
        user = get_user_model().objects.create_user(
            self.user_email, self.user_password, is_active=False)

        send_activation_email(user=user, request=request)
        self.assertEqual(len(mail.outbox), 1)


class EmailActivationTokenGeneratorTest(TestCase):
    user_email = 'user@example.com'
    user_password = 'pa$sw0Rd'

    def create_user(self):
        return get_user_model().objects.create_user(self.user_email, self.user_password)

    def test_make_token(self):
        """
        Ensure that we can make a token and that it is valid
        """
        user = self.create_user()

        token_generator = EmailActivationTokenGenerator()
        token = token_generator.make_token(user)
        self.assertTrue(token_generator.check_token(user, token))

    def test_bad_token(self):
        """
        Ensure bad activation keys are rejected
        """
        user = self.create_user()

        token_generator = EmailActivationTokenGenerator()
        bad_activation_keys = (
            'emailactivationtokengenerator',
            'emailactivation-tokengenerator',
            '3rd-bademailactivationkey'
        )
        for key in bad_activation_keys:
            self.assertFalse(token_generator.check_token(user, key))

    def test_timeout(self):
        """
        Ensure we can use the token after n days, but no greater.
        """
        # Uses a mocked version of EmailActivationTokenGenerator
        # so we can change the value of 'today'
        class Mocked(EmailActivationTokenGenerator):
            def __init__(self, today):
                self._today_val = today

            def _today(self):
                return self._today_val

        user = self.create_user()
        token_generator = EmailActivationTokenGenerator()
        token = token_generator.make_token(user)

        p1 = Mocked(date.today() + timedelta(settings.USERS_EMAIL_CONFIRMATION_TIMEOUT_DAYS))
        self.assertTrue(p1.check_token(user, token))

        p2 = Mocked(date.today() + timedelta(settings.USERS_EMAIL_CONFIRMATION_TIMEOUT_DAYS + 1))
        self.assertFalse(p2.check_token(user, token))
