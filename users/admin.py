from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _

from .conf import settings
from .forms import UserChangeForm, UserCreationForm
from .models import User
from .utils import send_activation_email

try:
    from django.contrib.admin.utils import model_ngettext
except ImportError:  # pragma: no cover
    from django.contrib.admin.util import model_ngettext


class UserModelFilter(admin.SimpleListFilter):
    """
    An admin list filter for the UserAdmin which enables
    filtering by its child models.
    """
    title = _('user type')
    parameter_name = 'user_type'

    def lookups(self, request, model_admin):
        user_types = set([user.user_type for user in model_admin.model.objects.all()])
        return [(user_type.id, user_type.name) for user_type in user_types]

    def queryset(self, request, queryset):
        try:
            value = int(self.value())
        except TypeError:
            value = None

        if value:
            return queryset.filter(user_type_id__exact=value)
        else:
            return queryset


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser',
                       'groups', 'user_permissions')
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )

    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'is_active')
    list_filter = (UserModelFilter, 'is_staff', 'is_superuser', 'is_active',)
    search_fields = ('email',)
    ordering = ('email',)
    actions = ('activate_users', 'send_activation_email', )
    readonly_fields = ('last_login', 'date_joined', )

    def get_queryset(self, request):
        # optimize queryset for list display.
        qs = self.model.base_objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def activate_users(self, request, queryset):
        """
        Activates the selected users, if they are not already
        activated.

        """
        n = 0
        for user in queryset:
            if not user.is_active:
                user.activate()
                n += 1
        self.message_user(
            request,
            _('Successfully activated %(count)d %(items)s.') %
            {'count': n, 'items': model_ngettext(self.opts, n)},  messages.SUCCESS)
    activate_users.short_description = _('Activate selected %(verbose_name_plural)s')

    def send_activation_email(self, request, queryset):
        """
        Send activation emails for the selected users, if they are not already
        activated.
        """
        n = 0
        for user in queryset:
            if not user.is_active and settings.USERS_VERIFY_EMAIL:
                send_activation_email(user=user, request=request)
                n += 1

        self.message_user(
            request, _('Activation emails sent to %(count)d %(items)s.') %
            {'count': n, 'items': model_ngettext(self.opts, n)},  messages.SUCCESS)

    send_activation_email.short_description = \
        _('Send activation emails to selected %(verbose_name_plural)s')


admin.site.register(User, UserAdmin)
