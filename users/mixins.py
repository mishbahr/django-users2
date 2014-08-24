from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import HttpResponseRedirect
from django.utils.encoding import force_text


class AccessMixin(object):
    """
    'Abstract' mixin that gives access mixins the same customizable
    functionality.
    """
    login_url = None
    raise_exception = False  # Default whether to raise an exception to none
    redirect_field_name = REDIRECT_FIELD_NAME  # Set by django.contrib.auth

    def get_login_url(self):
        """
        Override this method to customize the login_url.
        """
        login_url = self.login_url or settings.LOGIN_URL
        if not login_url:
            raise ImproperlyConfigured(
                'Define {0}.login_url or settings.LOGIN_URL or override '
                '{0}.get_login_url().'.format(self.__class__.__name__))

        return force_text(login_url)

    def get_redirect_field_name(self):
        """
        Override this method to customize the redirect_field_name.
        """
        if self.redirect_field_name is None:
            raise ImproperlyConfigured(
                '{0} is missing the '
                'redirect_field_name. Define {0}.redirect_field_name or '
                'override {0}.get_redirect_field_name().'.format(
                    self.__class__.__name__))
        return self.redirect_field_name


class LoginRequiredMixin(AccessMixin):
    """
    View mixin which verifies that the user is authenticated.

    NOTE:
        This should be the left-most mixin of a view, except when
        combined with CsrfExemptMixin - which in that case should
        be the left-most mixin.
    """
    redirect_unauthenticated_users = False

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            if self.raise_exception and not self.redirect_unauthenticated_users:
                raise PermissionDenied  # return a forbidden response
            else:
                return redirect_to_login(request.get_full_path(),
                                         self.get_login_url(),
                                         self.get_redirect_field_name())

        return super(LoginRequiredMixin, self).dispatch(
            request, *args, **kwargs)


class AnonymousRequiredMixin(object):
    """
    View mixin which redirects to a specified URL if authenticated.
    Can be useful if you wanted to prevent authenticated users from
    accessing signup pages etc.

    NOTE:
        This should be the left-most mixin of a view.

    Example Usage

        class SomeView(AnonymousRequiredMixin, ListView):
            ...
            # required
            authenticated_redirect_url = "/accounts/profile/"
            ...
    """
    authenticated_redirect_url = settings.LOGIN_REDIRECT_URL

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(self.get_authenticated_redirect_url())
        return super(AnonymousRequiredMixin, self).dispatch(
            request, *args, **kwargs)

    def get_authenticated_redirect_url(self):
        """ Return the reversed authenticated redirect url. """
        if not self.authenticated_redirect_url:
            raise ImproperlyConfigured(
                '{0} is missing an authenticated_redirect_url '
                'url to redirect to. Define '
                '{0}.authenticated_redirect_url or override '
                '{0}.get_authenticated_redirect_url().'.format(
                    self.__class__.__name__))
        return self.authenticated_redirect_url


class SuperuserRequiredMixin(AccessMixin):
    """
    Mixin allows you to require a user with `is_superuser` set to True.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:  # If the user is a standard user,
            if self.raise_exception:  # *and* if an exception was desired
                raise PermissionDenied  # return a forbidden response.
            else:
                return redirect_to_login(request.get_full_path(),
                                         self.get_login_url(),
                                         self.get_redirect_field_name())

        return super(SuperuserRequiredMixin, self).dispatch(
            request, *args, **kwargs)


class StaffMemberRequiredMixin(AccessMixin):
    """
    Mixin allows you to require a user with `is_staff` set to True.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:  # If the request's user is not staff,
            if self.raise_exception:  # *and* if an exception was desired
                raise PermissionDenied  # return a forbidden response
            else:
                return redirect_to_login(request.get_full_path(),
                                         self.get_login_url(),
                                         self.get_redirect_field_name())

        return super(StaffMemberRequiredMixin, self).dispatch(
            request, *args, **kwargs)


class UserPassesTestMixin(AccessMixin):
    """
    CBV Mixin allows you to define test that every user should pass
    to get access into view.

    Class Settings
        `test_func` - This is required to be a method that takes user
            instance and return True or False after checking conditions.
        `login_url` - the login url of site
        `redirect_field_name` - defaults to "next"
        `raise_exception` - defaults to False - raise 403 if set to True
    """

    def test_func(self, user):
        raise NotImplementedError(
            '{0} is missing implementation of the '
            'test_func method. You should write one.'.format(
                self.__class__.__name__))

    def get_test_func(self):
        return getattr(self, 'test_func')

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()(request.user)

        if not user_test_result:  # If user don't pass the test
            if self.raise_exception:  # *and* if an exception was desired
                raise PermissionDenied
            else:
                return redirect_to_login(request.get_full_path(),
                                         self.get_login_url(),
                                         self.get_redirect_field_name())
        return super(UserPassesTestMixin, self).dispatch(
            request, *args, **kwargs)
