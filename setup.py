#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os
import sys

import users

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = users.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

readme = codecs.open('README.rst', 'r', 'utf-8').read()

setup(
    name='django-users2',
    version=version,
    description="""Custom user model for django >=1.11 with support for multiple user types""",
    long_description=readme,
    author='Mishbah Razzaque',
    author_email='mishbahx@gmail.com',
    url='https://github.com/mishbahr/django-users2',
    packages=[
        'users',
    ],
    include_package_data=True,
    install_requires=[
        'django>=1.11',
        'django-model-utils',
        'django-appconf',
    ],
    license="BSD",
    zip_safe=False,
    keywords='django-users2',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
