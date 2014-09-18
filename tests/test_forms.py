#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _

from users.forms import (RegistrationFormHoneypot,
                         RegistrationFormTermsOfService, UserChangeForm,
                         UserCreationForm)


class UserCreationFormTest(TestCase):

    def test_user_already_exists(self):
        get_user_model().objects.create_user('testuser@example.com', 'Pa$sw0rd')

        data = {
            'email': 'testuser@example.com',
            'password1': 'Pa$sw0rd',
            'password2': 'Pa$sw0rd',
        }
        form = UserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form['email'].errors,
                         [force_text(form.error_messages['duplicate_email'])])

    def test_invalid_email(self):
        data = {
            'email': 'testuser',
            'password1': 'Pa$sw0rd',
            'password2': 'Pa$sw0rd',
        }
        form = UserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn(_('Enter a valid email address.'), form['email'].errors)

    def test_password_verification(self):
        # The verification password is incorrect.
        data = {
            'email': 'testuser@example.com',
            'password1': 'Pa$sw0rd1',
            'password2': 'Pa$sw0rd2',
        }
        form = UserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form['password2'].errors,
                         [force_text(form.error_messages['password_mismatch'])])

    def test_password_is_not_saved_raw(self):
        raw_password = 'Pa$sw0rd2'
        data = {
            'email': 'testuser@example.com',
            'password1': raw_password,
            'password2': raw_password,
        }
        form = UserCreationForm(data)
        user = form.save()
        self.assertNotEqual(raw_password, user.password)

    def test_valid_user_are_saved(self):
        data = {
            'email': 'validuser@example.com',
            'password1': 'Pa$sw0rd',
            'password2': 'Pa$sw0rd',
        }
        form = UserCreationForm(data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(repr(user), '<%s: validuser@example.com>' % get_user_model().__name__)


class UserChangeFormTest(TestCase):

    def test_username_validity(self):
        user = get_user_model().objects.create_user('testuser@example.com', 'Pa$sw0rd')
        data = {
            'email': 'invalid-email'
        }
        form = UserChangeForm(data, instance=user)
        self.assertFalse(form.is_valid())
        self.assertIn(_('Enter a valid email address.'), form['email'].errors)

    def test_unsuable_password(self):
        user = get_user_model().objects.create_user('testuser@example.com', 'Pa$sw0rd')
        user.set_unusable_password()
        user.save()
        form = UserChangeForm(instance=user)
        self.assertIn(_('No password set.'), form.as_table())


class RegistrationFormTermsOfServiceTest(TestCase):

    def test_registration_form_with_tos_checkbox_validates(self):
        data = {
            'email': 'testuser@example.com',
            'password1': 'Pa$sw0rd',
            'password2': 'Pa$sw0rd',
            'tos': True
        }
        form = RegistrationFormTermsOfService(data=data)
        self.assertTrue(form.is_valid())

    def test_registration_form_with_tos_checkbox_fails(self):
        data = {
            'email': 'testuser@example.com',
            'password1': 'Pa$sw0rd',
            'password2': 'Pa$sw0rd',
        }
        form = RegistrationFormTermsOfService(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['tos'], [u'You must agree to the terms to register'])


class RegistrationFormHoneypotTest(TestCase):
    def test_registration_form_with_honeypot_field(self):
        data = {
            'email': 'testuser@example.com',
            'password1': 'Pa$sw0rd',
            'password2': 'Pa$sw0rd',
        }
        form = RegistrationFormHoneypot(data=data)
        self.assertTrue(form.is_valid())

    def test_registration_form_with_honeypot_field_fails_as_expected(self):
        data = {
            'email': 'testuser@example.com',
            'password1': 'Pa$sw0rd',
            'password2': 'Pa$sw0rd',
            'accept_terms': True
        }
        form = RegistrationFormHoneypot(data=data)
        self.assertFalse(form.is_valid())
