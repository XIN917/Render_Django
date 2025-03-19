from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django import forms

User = get_user_model()

class CustomUserCreationForm(forms.ModelForm):
    """ Custom form to allow user creation with a default password. """
    
    class Meta:
        model = User
        fields = ('full_name', 'email', 'role', 'is_staff', 'is_active')

    def save(self, commit=True):
        """ Ensure default password is set when creating a user. """
        user = super().save(commit=False)
        if not user.password:  # If no password is provided, set default
            user.set_password("12345678")
        if commit:
            user.save()
        return user

class CustomUserAdmin(UserAdmin):
    """ Custom admin panel for managing users. """
    list_display = ('id', 'full_name', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('full_name', 'email')
    ordering = ('id',)

    add_form = CustomUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('full_name', 'email', 'role', 'is_staff', 'is_active'),
        }),
    )

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('role', 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),    
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    def save_model(self, request, obj, form, change):
        """ Ensure the default password is set when creating a new user and enforce role updates. """
        if not obj.password:  # If no password is set, use the default one
            obj.set_password("12345678")
        if change and 'role' in form.changed_data:
            obj.save(update_fields=['role'])  # Force role update in the database
        else:
            obj.save()

admin.site.register(User, CustomUserAdmin)
