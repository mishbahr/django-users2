from django.db import models
from django.utils.translation import ugettext_lazy as _

from users.models import User


class Customer(User):
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)

    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')
