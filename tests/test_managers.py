#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.test import TestCase

from example.models import Customer


class UserManagerTest(TestCase):

    user_email = 'user@example.com'
    user_password = 'pa$sw0Rd'

    def test_create_user(self):
        user = get_user_model().objects.create_user(self.user_email)
        self.assertEqual(user.email, self.user_email)
        self.assertFalse(user.has_usable_password())
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser(
            self.user_email, self.user_password)

        self.assertEqual(user.email, self.user_email)
        self.assertTrue(user.check_password, self.user_password)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_inactive_user_creation(self):
        # Create deactivated user
        user = get_user_model().objects.create_user(
            self.user_email, self.user_password, is_active=False)
        self.assertFalse(user.is_active)

    def test_staff_user_creation(self):
        # Create staff user
        user = get_user_model().objects.create_user(
            self.user_email, self.user_password, is_staff=True)
        self.assertTrue(user.is_staff)

    def test_empty_username(self):
        self.assertRaises(ValueError, get_user_model().objects.create_user, email='')

    def test_automatic_downcasting_of_inherited_user_models(self):
        get_user_model().objects.create_superuser(
            self.user_email, self.user_password)
        Customer.objects.create_user('customer@example.com', 'cu$t0meR')
        self.assertQuerysetEqual(
            get_user_model().objects.all(),
            ['<User: user@example.com>', '<Customer: customer@example.com>'], ordered=False)
