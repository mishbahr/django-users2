=============================
django-users2
=============================

.. image:: http://img.shields.io/travis/mishbahr/django-users2.svg?style=flat-square
    :target: https://travis-ci.org/mishbahr/django-users2/

.. image:: http://img.shields.io/pypi/v/django-users2.svg?style=flat-square
    :target: https://pypi.python.org/pypi/django-users2/
    :alt: Latest Version

.. image:: http://img.shields.io/pypi/dm/django-users2.svg?style=flat-square
    :target: https://pypi.python.org/pypi/django-users2/
    :alt: Downloads

.. image:: http://img.shields.io/pypi/l/django-users2.svg?style=flat-square
    :target: https://pypi.python.org/pypi/django-users2/
    :alt: License

.. image:: http://img.shields.io/coveralls/mishbahr/django-users2.svg?style=flat-square
  :target: https://coveralls.io/r/mishbahr/django-users2?branch=master


Custom user model for django >=1.5 with support for multiple user types and
lots of other awesome utils (mostly borrowed from other projects). If you are
using django < 1.11, please install v0.2.1 or earlier (`pip install
django-users2<=0.2.1`).

Features
--------

* email as username for authentication (barebone extendable user models)
* support for multiple user types (using the awesome django-model-utils)
* automatically creates superuser after syncdb/migrations (really handy during the initial development phases)
* built in emails/passwords validators (with lots of customisable options)
* prepackaged with all the templates, including additional templates required by views in ``django.contrib.auth`` (for a painless signup process)


Documentation
-------------

The full documentation is at https://django-users2.readthedocs.org.

Quickstart
----------

1. Install `django-users2`::

    pip install django-users2

2. Add `django-users2` to `INSTALLED_APPS`::

    INSTALLED_APPS = (
        ...
        'django.contrib.auth',
    	'django.contrib.sites',
        'users',
        ...
    )

3. Set your `AUTH_USER_MODEL` setting to use ``users.User``::

    AUTH_USER_MODEL = 'users.User'

4. Once you’ve done this, run the ``migrate`` command to install the model used by this package::

    python manage.py migrate

5. Add the `django-users2` URLs to your project’s URLconf as follows::

    urlpatterns = patterns('',
        ...
        url(r'^accounts/', include('users.urls')),
        ...
    )

which sets up URL patterns for the views in django-users2 as well as several useful views in django.contrib.auth (e.g. login, logout, password change/reset)


Configuration
-----------------------
Set ``USERS_VERIFY_EMAIL = True`` to enable email verification for registered users. 

When a new ``User`` object is created, with its ``is_active`` field set to ``False``, an activation key is generated, and an email is sent to the user containing a link to click to activate the account::

    USERS_VERIFY_EMAIL = False

Upon clicking the activation link, the new account is made active (i.e. ``is_active`` field is set to ``True``); after this, the user can log in. Optionally, you can automatically login the user after successful activation::
    
    USERS_AUTO_LOGIN_ON_ACTIVATION = True

This is the number of days the users will have, to activate their accounts after registering:: 

   USERS_EMAIL_CONFIRMATION_TIMEOUT_DAYS = 3

Automatically create django ``superuser`` after ``syncdb``, by default this option is enabled when ``settings.DEBUG = True``. 

You can customise the email/password by overriding ``USERS_SUPERUSER_EMAIL`` and ``USERS_SUPERUSER_PASSWORD`` settings (highly recommended)::

    USERS_CREATE_SUPERUSER = settings.DEBUG
    USERS_SUPERUSER_EMAIL = 'superuser@djangoproject.com'
    USERS_SUPERUSER_PASSWORD = 'django'  

Prevent automated registration by spambots, by enabling a hidden (using css) honeypot field::

    USERS_SPAM_PROTECTION = True

Prevent user registrations by setting ``USERS_REGISTRATION_OPEN = False``::

	USERS_REGISTRATION_OPEN = True


Settings for validators, that check the strength of user specified passwords::
    
    # Specifies minimum length for passwords:
    USERS_PASSWORD_MIN_LENGTH = 5

    #Specifies maximum length for passwords:
    USERS_PASSWORD_MAX_LENGTH = None
	
Optionally, the complexity validator, checks the password strength::

	USERS_CHECK_PASSWORD_COMPLEXITY = True

Specify number of characters within various sets that a password must contain::

	USERS_PASSWORD_POLICY = {
		'UPPER': 0,       # Uppercase 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
		'LOWER': 0,       # Lowercase 'abcdefghijklmnopqrstuvwxyz'
		'DIGITS': 0,      # Digits '0123456789'
		'PUNCTUATION': 0  # Punctuation """!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
	}

Allow/disallow registration using emails addresses from specific domains::
 
    USERS_VALIDATE_EMAIL_DOMAIN = True

List of disallowed domains::

    USERS_EMAIL_DOMAINS_BLACKLIST = []

For example, ``USERS_EMAIL_DOMAINS_BLACKLIST = ['mailinator.com']`` will block all visitors from using mailinator.com email addresses to register.
    
List of allowed domains::

    USERS_EMAIL_DOMAINS_WHITELIST = []

For example, ``USERS_EMAIL_DOMAINS_WHITELIST = ['ljworld.com']`` will only allow user registration with ljworld.com domains.
