from django.conf.urls import url
from django.contrib.auth.views import (login, logout, password_change,
                                       password_change_done, password_reset,
                                       password_reset_complete,
                                       password_reset_confirm,
                                       password_reset_done)

from .views import (activate, activation_complete, register,
                    registration_closed, registration_complete)

urlpatterns = [
    url(r'^register/$', register, name='users_register'),
    url(r'^register/closed/$', registration_closed, name='users_registration_closed'),
    url(r'^register/complete/$', registration_complete, name='users_registration_complete'),
    url(r'^activate/complete/$', activation_complete, name='users_activation_complete'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        activate, name='users_activate'),

    url(r'^login/$', login, {'template_name': 'users/login.html'}, name='users_login'),
    url(r'^logout/$', logout, {'template_name': 'users/logout.html'}, name='users_logout'),
    url(r'^password_change/$', password_change,
        {
            'template_name': 'users/password_change_form.html',
            'post_change_redirect': 'users_password_change_done'
        },
        name='users_password_change'),
    url(r'^password_change/done/$', password_change_done,
        {'template_name': 'users/password_change_done.html'},
        name='users_password_change_done'),
    url(r'^password_reset/$', password_reset,
        {
            'template_name': 'users/password_reset_form.html',
            'email_template_name': 'users/password_reset_email.html',
            'subject_template_name': 'users/password_reset_subject.html',
            'post_reset_redirect': 'users_password_reset_done'
        },
        name='users_password_reset'),
    url(r'^password_reset/done/$', password_reset_done,
        {'template_name': 'users/password_reset_done.html'},
        name='users_password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        password_reset_confirm,
        {
            'template_name': 'users/password_reset_confirm.html',
            'post_reset_redirect': 'users_password_reset_complete'
        },
        name='users_password_reset_confirm'),
    url(r'^reset/done/$', password_reset_complete,
        {'template_name': 'users/password_reset_complete.html'},
        name='users_password_reset_complete'),
]
