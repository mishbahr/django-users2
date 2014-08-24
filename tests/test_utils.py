#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.core import mail
from django.test.utils import override_settings
from django.contrib.auth import get_user_model

from users.utils import auto_create_superuser, send_activation_email


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

