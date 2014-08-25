#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib import admin


class AdminTest(TestCase):

    user_email = 'user@example.com'
    user_password = 'pa$sw0Rd'

    def setUp(self):
        get_user_model().objects.create_superuser(self.user_email, self.user_password)

        self.assertTrue(self.client.login(
            username=self.user_email, password=self.user_password),
            'Failed to login user %s' % self.user_email)

    def test_admin(self):
        # Force Django to load ModelAdmin objects
        admin.autodiscover()

    def tearDown(self):
        self.client.logout()
