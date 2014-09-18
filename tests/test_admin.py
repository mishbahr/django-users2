#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core import mail
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings

from users.admin import UserAdmin


class AdminTest(TestCase):

    user_email = 'user@example.com'
    user_password = 'pa$sw0Rd'

    def setUp(self):
        get_user_model().objects.create_superuser(self.user_email, self.user_password)

        self.assertTrue(self.client.login(
            username=self.user_email, password=self.user_password),
            'Failed to login user %s' % self.user_email)

        get_user_model().objects.create_user('user1@example.com', 'pa$sw0Rd1', is_active=False)

        factory = RequestFactory()
        self.request = factory.get('/admin')

        # Hack to test this function as it calls 'messages.add'
        # See https://code.djangoproject.com/ticket/17971
        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def test_get_queryset(self):
        user_admin = UserAdmin(get_user_model(), AdminSite())
        self.assertQuerysetEqual(
            user_admin.get_queryset(self.request),
            ['<User: user@example.com>', '<User: user1@example.com>'], ordered=False)

    @override_settings(USERS_VERIFY_EMAIL=True)
    def test_send_activation_email(self):
        user_admin = UserAdmin(get_user_model(), AdminSite())

        qs = get_user_model().objects.all()
        user_admin.send_activation_email(self.request, qs)
        # we created 1 inactive user, so there should be one email in outbox
        self.assertEqual(len(mail.outbox), 1)

    def test_activate_users(self):
        user_admin = UserAdmin(get_user_model(), AdminSite())

        qs = get_user_model().objects.all()
        user_admin.activate_users(self.request, qs)
        # both users should be active
        self.assertEqual(get_user_model().objects.filter(is_active=True).count(), 2)
        # superuser is automatically activated. so we test the attribute for user1@example.com
        user = get_user_model().objects.get(email='user1@example.com')
        self.assertTrue(user.is_active)

    def tearDown(self):
        self.client.logout()
