from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.urls import reverse
from django.shortcuts import redirect, resolve_url
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from .compat import urlsafe_base64_decode
from .conf import settings
from .signals import user_activated, user_registered
from .utils import EmailActivationTokenGenerator, send_activation_email

try:
    from django.contrib.sites.shortcuts import get_current_site
except ImportError:  # pragma: no cover
    from django.contrib.sites.models import get_current_site


if settings.USERS_SPAM_PROTECTION:  # pragma: no cover
    from .forms import RegistrationFormHoneypot as RegistrationForm
else:
    from .forms import RegistrationForm


@csrf_protect
@never_cache
def register(request,
             template_name='users/registration_form.html',
             activation_email_template_name='users/activation_email.html',
             activation_email_subject_template_name='users/activation_email_subject.html',
             activation_email_html_template_name=None,
             registration_form=RegistrationForm,
             registered_user_redirect_to=None,
             post_registration_redirect=None,
             activation_from_email=None,
             current_app=None,
             extra_context=None):

    if registered_user_redirect_to is None:
        registered_user_redirect_to = getattr(settings, 'LOGIN_REDIRECT_URL')

    if request.user.is_authenticated:
            return redirect(registered_user_redirect_to)

    if not settings.USERS_REGISTRATION_OPEN:
        return redirect(reverse('users_registration_closed'))

    if post_registration_redirect is None:
        post_registration_redirect = reverse('users_registration_complete')

    if request.method == 'POST':
        form = registration_form(request.POST)
        if form.is_valid():
            user = form.save()
            if settings.USERS_AUTO_LOGIN_AFTER_REGISTRATION:
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
            elif not user.is_active and settings.USERS_VERIFY_EMAIL:
                opts = {
                    'user': user,
                    'request': request,
                    'from_email': activation_from_email,
                    'email_template': activation_email_template_name,
                    'subject_template': activation_email_subject_template_name,
                    'html_email_template': activation_email_html_template_name,
                }
                send_activation_email(**opts)
                user_registered.send(sender=user.__class__, request=request, user=user)
            return redirect(post_registration_redirect)
    else:
        form = registration_form()

    current_site = get_current_site(request)

    context = {
        'form': form,
        'site': current_site,
        'site_name': current_site.name,
        'title': _('Register'),
    }

    if extra_context is not None:  # pragma: no cover
        context.update(extra_context)
    return TemplateResponse(request, template_name, context)


def registration_closed(request,
                        template_name='users/registration_closed.html',
                        current_app=None,
                        extra_context=None):
    context = {
        'title': _('Registration closed'),
    }
    if extra_context is not None:  # pragma: no cover
        context.update(extra_context)
    return TemplateResponse(request, template_name, context)


def registration_complete(request,
                          template_name='users/registration_complete.html',
                          current_app=None,
                          extra_context=None):
    context = {
        'login_url': resolve_url(settings.LOGIN_URL),
        'title': _('Registration complete'),
    }
    if extra_context is not None:  # pragma: no cover
        context.update(extra_context)
    return TemplateResponse(request, template_name, context)


@never_cache
def activate(request,
             uidb64=None,
             token=None,
             template_name='users/activate.html',
             post_activation_redirect=None,
             current_app=None,
             extra_context=None):

    context = {
        'title': _('Account activation '),
    }

    if post_activation_redirect is None:
        post_activation_redirect = reverse('users_activation_complete')

    UserModel = get_user_model()
    assert uidb64 is not None and token is not None

    token_generator = EmailActivationTokenGenerator()

    try:
        uid = urlsafe_base64_decode(uidb64)
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        user.activate()
        user_activated.send(sender=user.__class__, request=request, user=user)
        if settings.USERS_AUTO_LOGIN_ON_ACTIVATION:
            user.backend = 'django.contrib.auth.backends.ModelBackend'  # todo - remove this hack
            login(request, user)
            messages.info(request, 'Thanks for registering. You are now logged in.')
        return redirect(post_activation_redirect)
    else:
        title = _('Email confirmation unsuccessful')
        context = {
            'title': title,
        }

    if extra_context is not None:  # pragma: no cover
        context.update(extra_context)
    return TemplateResponse(request, template_name, context)


def activation_complete(request,
                        template_name='users/activation_complete.html',
                        current_app=None,
                        extra_context=None):
    context = {
        'title': _('Activation complete'),
    }
    if extra_context is not None:  # pragma: no cover
        context.update(extra_context)
    return TemplateResponse(request, template_name, context)
