#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase


class TestUsersModels(TestCase):

    user_email = 'user@example.com'
    user_password = 'pa$sw0Rd'

    def create_user(self):
        return get_user_model().objects.create_user(self.user_email, self.user_password)

    def test_user_creation(self):
        user = self.create_user()

        self.assertEqual(get_user_model().objects.all().count(), 1)
        self.assertEqual(user.email, self.user_email)

        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_user_get_full_name(self):
        user = self.create_user()
        self.assertEqual(user.get_full_name(), self.user_email)

    def test_user_get_short_name(self):
        user = self.create_user()
        self.assertEqual(user.get_short_name(), self.user_email)

    def test_email_user(self):
        # Email definition
        subject = 'email subject'
        message = 'email message'
        from_email = 'from@example.com'

        user = self.create_user()

        # Test that no message exists
        self.assertEqual(len(mail.outbox), 0)

        # Send test email
        user.email_user(subject, message, from_email)

        # Test that one message has been sent
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the email is correct
        self.assertEqual(mail.outbox[0].subject, subject)
        self.assertEqual(mail.outbox[0].body, message)
        self.assertEqual(mail.outbox[0].from_email, from_email)
        self.assertEqual(mail.outbox[0].to, [user.email])

    def test_user_activation(self):
        user = get_user_model().objects.create_user(
            self.user_email, self.user_password, is_active=False)
        # check user is not active by default
        self.assertFalse(user.is_active)
        # activate user
        user.activate()
        self.assertTrue(user.is_active)

    def test_(self):
        user = self.create_user()
        self.assertIsNotNone(user.user_type)
