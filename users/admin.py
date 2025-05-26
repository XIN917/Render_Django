from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django import forms
from django.core.exceptions import ValidationError
from profiles.models import Profile

User = get_user_model()

class CustomUserCreationForm(forms.ModelForm):
    """ Custom form to allow user creation with a default password. """
    
    class Meta:
        model = User
        fields = ('full_name', 'email', 'role', 'is_staff', 'is_active')

    def save(self, commit=True):
        """Ensure default password is set when creating a user."""
        user = super().save(commit=False)
        if not user.password:
            user.set_password("12345678")
        if commit:
            user.save()
        return user

class CustomUserChangeForm(forms.ModelForm):
    """Form for updating users."""
    
    class Meta:
        model = User
        fields = ('full_name', 'email', 'role', 'is_staff', 'is_active')

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = ('institution', 'bio', 'photo')

    def clean(self):
        cleaned_data = super().clean()
        # Validate that if user role is teacher, institution must be set
        if self.instance.user.role == User.TEACHER and not cleaned_data.get('institution'):
            raise ValidationError("Teachers must have an associated institution.")
        return cleaned_data

class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ('id', 'full_name', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('full_name', 'email')
    ordering = ('id',)

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

    inlines = (ProfileInline,)

    def save_model(self, request, obj, form, change):
        if not obj.password:
            obj.set_password("12345678")
        super().save_model(request, obj, form, change)

admin.site.register(User, CustomUserAdmin)
