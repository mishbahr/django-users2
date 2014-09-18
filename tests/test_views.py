#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from users.forms import RegistrationForm, RegistrationFormHoneypot


class RegisterViewTest(TestCase):
    user_data = {
        'email': 'user@example.com',
        'password1': 'pa$sw0Rd',
        'password2': 'pa$sw0Rd'
    }

    @override_settings(USERS_REGISTRATION_OPEN=True)
    def test_registration_allowed(self):
        resp = self.client.get(reverse('users_register'))
        self.assertEqual(200, resp.status_code)

    @override_settings(USERS_REGISTRATION_OPEN=False)
    def test_registration_closed(self):
        resp = self.client.get(reverse('users_register'))
        self.assertRedirects(resp, reverse('users_registration_closed'))

    @override_settings(USERS_SPAM_PROTECTION=False)
    def test_registration_form(self):
        resp = self.client.get(reverse('users_register'))
        self.assertEqual(200, resp.status_code)
        self.failUnless(isinstance(resp.context['form'], RegistrationForm))

    @override_settings(USERS_SPAM_PROTECTION=True)
    def test_registration_form_with_honeypot(self):
        resp = self.client.get(reverse('users_register'))
        self.assertEqual(200, resp.status_code)
        self.failUnless(isinstance(resp.context['form'], RegistrationFormHoneypot))

    def test_registration(self):
        resp = self.client.post(reverse('users_register'), self.user_data)
        self.assertRedirects(resp, reverse('users_registration_complete'))

    def test_registration_created_new_user(self):
        resp = self.client.post(reverse('users_register'), self.user_data)
        self.assertEqual(get_user_model().objects.all().count(), 1)

    @override_settings(LOGIN_REDIRECT_URL=reverse('users_registration_complete'))
    def test_authenticated_users_are_redirected(self):
        user = get_user_model().objects.create_user(
            self.user_data['email'], self.user_data['password1'], is_active=True)
        login = self.client.login(
            username=self.user_data['email'],
            password=self.user_data['password1'])
        self.assertEqual(login, True)
        resp = self.client.post(reverse('users_register'), self.user_data)
        self.assertRedirects(resp, reverse('users_registration_complete'))

    @override_settings(USERS_VERIFY_EMAIL=True)
    def test_registered_user_is_not_active(self):
        resp = self.client.post(reverse('users_register'), self.user_data)
        new_user = get_user_model().objects.get(email=self.user_data['email'])
        self.failIf(new_user.is_active)

    @override_settings(USERS_VERIFY_EMAIL=True)
    def test_activation_email_was_sent(self):
        resp = self.client.post(reverse('users_register'), self.user_data)
        self.assertEqual(len(mail.outbox), 1)


class ActivationViewTest(TestCase):
    user_data = {
        'email': 'user@example.com',
        'password1': 'pa$sw0Rd',
        'password2': 'pa$sw0Rd'
    }

    @override_settings(USERS_VERIFY_EMAIL=True)
    def test_activation_view(self):
        self.client.post(reverse('users_register'), self.user_data)
        activation_email = mail.outbox[0]
        urlmatch = re.search(r'https?://[^/]*(/.*activate/\S*)', activation_email.body)
        self.assertTrue(urlmatch is not None, 'No URL found in sent email')
        resp = self.client.get(urlmatch.groups()[0])
        self.assertRedirects(resp, reverse('users_activation_complete'))

        new_user = get_user_model().objects.get(email=self.user_data['email'])
        self.assertTrue(new_user.is_active)

    @override_settings(USERS_VERIFY_EMAIL=True)
    def test_activation_view_fails_as_expected(self):
        url = reverse('users_activate', kwargs={
            'uidb64': 'MQ',
            'token': 'bad-69b5cdcd57c6854d1b04'
        })
        resp = self.client.get(url)
        self.assertEqual(200, resp.status_code)
        self.failUnless(resp.context['title'], 'Email confirmation unsuccessful')
