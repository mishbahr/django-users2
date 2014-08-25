=============================
django-users2
=============================

.. image:: https://travis-ci.org/mishbahr/django-users2.svg?branch=master
    :target: https://travis-ci.org/mishbahr/django-users2/

.. image:: https://pypip.in/version/django-users2/badge.svg
    :target: https://pypi.python.org/pypi/django-users2/
    :alt: Latest Version

.. image:: https://pypip.in/download/django-users2/badge.svg
    :target: https://pypi.python.org/pypi/django-users2/
    :alt: Downloads

.. image:: https://pypip.in/license/django-users2/badge.svg
    :target: https://pypi.python.org/pypi/django-users2/
    :alt: License

.. image:: https://pypip.in/py_versions/django-users2/badge.svg
    :target: https://pypi.python.org/pypi/django-users2/
    :alt: Supported Python versions


.. image:: https://coveralls.io/repos/mishbahr/django-users2/badge.png?branch=master
  :target: https://coveralls.io/r/mishbahr/django-users2?branch=master


Custom user model for django >=1.5 with support for multiple user types and
lots of other awesome utils (mostly borrowed from other projects).

Features
--------

* email as username for authentication (barebone extendable user models)
* support for multiple user types (using the awesome django-model-utils)
* automatically creates superuser after syncdb (really handy during the initial development phases)
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
        'users',
        ...
    )

3. Set your `AUTH_USER_MODEL` setting to use ``users.User``::

    AUTH_USER_MODEL = 'users.User'

4. Once you’ve done this, run the syncdb command to install the model used by this package::

    python manage.py syncdb

5. Add the `django-users2` URLs to your project’s URLconf as follows::

    urlpatterns = patterns('',
        ...
        url(r'^accounts/', include('users.urls')),
        ...
    )

which sets up URL patterns for the views in django-users2 as well as several useful views in django.contrib.auth (e.g. login, logout, password change/reset)
