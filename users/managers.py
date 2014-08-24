from django.utils import timezone
from django.contrib.auth.models import BaseUserManager

from model_utils.managers import InheritanceQuerySet

from .conf import settings


class UserManager(BaseUserManager):

    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):

        users_auto_activate = not settings.USERS_VERIFY_EMAIL
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)

        is_active = extra_fields.pop('is_active', users_auto_activate)
        user = self.model(email=email, is_staff=is_staff, is_active=is_active,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):

        is_staff = extra_fields.pop('is_staff', False)
        return self._create_user(email, password, is_staff, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True,
                                 **extra_fields)


class UserInheritanceManager(UserManager):
    def get_queryset(self):
        return InheritanceQuerySet(self.model).select_subclasses()
