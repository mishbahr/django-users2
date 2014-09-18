#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from django.test import TestCase
from django.test.utils import override_settings

from users.fields import (ComplexityValidator, EmailDomainValidator,
                          LengthValidator)


class LengthValidatorTest(TestCase):

    @override_settings(USERS_PASSWORD_MIN_LENGTH=6, USERS_PASSWORD_MAX_LENGTH=20)
    def setUp(self):
        self.length_validator = LengthValidator()

    def test_password_length_validator_min_length(self):
        value = 'abc'
        try:
            self.length_validator(value)
        except forms.ValidationError:
            pass
        else:
            self.fail('ValidationError not raised when validating \'%s\'' % value)

    def test_password_length_validator_max_length(self):
        value = 'qwertyuiopasdfghjklzxcvbnm'
        try:
            self.length_validator(value)
        except forms.ValidationError:
            pass
        else:
            self.fail('ValidationError not raised when validating \'%s\'' % value)


class ComplexityValidatorTest(TestCase):
    password_policy = {
        'UPPER': 1,
        'LOWER': 1,
        'DIGITS': 1,
        'PUNCTUATION': 1
    }

    @override_settings(USERS_PASSWORD_POLICY={'UPPER': 1})
    def test_complexity_validator_fails_no_uppercase(self):
        complexity_validator = ComplexityValidator()
        value = 'password'
        try:
            complexity_validator(value)
        except forms.ValidationError:
            pass
        else:
            self.fail('ValidationError not raised when validating \'%s\'' % value)

    @override_settings(USERS_PASSWORD_POLICY={'LOWER': 1})
    def test_complexity_validator_fails_no_lowercase(self):
        complexity_validator = ComplexityValidator()
        value = 'PASSWORD'
        try:
            complexity_validator(value)
        except forms.ValidationError:
            pass
        else:
            self.fail('ValidationError not raised when validating \'%s\'' % value)

    @override_settings(USERS_PASSWORD_POLICY={'DIGITS': 1})
    def test_complexity_validator_fails_no_digit(self):
        complexity_validator = ComplexityValidator()
        value = 'password'
        try:
            complexity_validator(value)
        except forms.ValidationError:
            pass
        else:
            self.fail('ValidationError not raised when validating \'%s\'' % value)

    @override_settings(USERS_PASSWORD_POLICY={'PUNCTUATION': 1})
    def test_complexity_validator_fails_no_symbol(self):
        complexity_validator = ComplexityValidator()
        value = 'password'
        try:
            complexity_validator(value)
        except forms.ValidationError:
            pass
        else:
            self.fail('ValidationError not raised when validating \'%s\'' % value)

    @override_settings(USERS_PASSWORD_POLICY=password_policy)
    def test_complexity_validator_success(self):
        complexity_validator = ComplexityValidator()
        value = 'Pas$word1'
        try:
            complexity_validator(value)
        except forms.ValidationError:
            self.fail('ValidationError raised when validating \'%s\'' % value)


class EmailDomainValidatorTest(TestCase):
    domains_blacklist = ('mailinator.com', )
    domains_whitelist = ('djangoproject.com', )

    @override_settings(USERS_EMAIL_DOMAINS_WHITELIST=domains_whitelist)
    def test_email_domain_validator_with_white_list(self):
        email_domain_validator = EmailDomainValidator()
        value = 'user@example.com'
        try:
            email_domain_validator(value)
        except forms.ValidationError:
            pass
        else:
            self.fail('ValidationError not raised when validating \'%s\'' % value)

    @override_settings(USERS_EMAIL_DOMAINS_BLACKLIST=domains_blacklist)
    def test_email_domain_validator_with_black_list(self):
        email_domain_validator = EmailDomainValidator()
        value = 'spammer@mailinator.com'
        try:
            email_domain_validator(value)
        except forms.ValidationError:
            pass
        else:
            self.fail('ValidationError not raised when validating \'%s\'' % value)
